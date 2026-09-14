"""S3RAPHIM v2 ML pipeline — split by flight_id when available."""
from pathlib import Path
import sys, json

CSV_FILE, MODEL_FILE, METRICS_FILE = "adsb_thesis_features.csv", "s3raphim_model.joblib", "s3raphim_metrics.json"
FEATURE_COLS = ["altitude","velocity","heading","latitude","longitude","altitude_rate","heading_change","acceleration"]
TARGET, SEED, THRESH = "abnormal", 42, 100

def main():
    try:
        import pandas as pd, joblib
        from sklearn.model_selection import GroupShuffleSplit, train_test_split, cross_val_score
        from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import accuracy_score, roc_auc_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
    except ImportError:
        print("pip install scikit-learn pandas joblib"); sys.exit(1)
    if not Path(CSV_FILE).exists():
        print(f"Missing {CSV_FILE}"); sys.exit(1)
    df = pd.read_csv(CSV_FILE)
    X, y = df[FEATURE_COLS].fillna(0), df[TARGET].astype(int)
    print(f"Rows={len(df):,} normal={(y==0).sum():,} abnormal={(y==1).sum():,}")
    if y.nunique()<2: print("Need both classes"); sys.exit(1)

    if "flight_id" in df.columns and df["flight_id"].nunique()>1:
        gss = GroupShuffleSplit(n_splits=1, test_size=0.3, random_state=SEED)
        tr, te = next(gss.split(X, y, groups=df["flight_id"]))
        X_train, X_test, y_train, y_test = X.iloc[tr], X.iloc[te], y.iloc[tr], y.iloc[te]
        print("Split: by flight_id (leakage-safer)")
    else:
        X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.3,stratify=y,random_state=SEED)
        print("Split: stratified rows")

    def mets(yt,yp,prob=None):
        m={"accuracy":float(accuracy_score(yt,yp)),"precision":float(precision_score(yt,yp,zero_division=0)),
           "recall":float(recall_score(yt,yp,zero_division=0)),"f1":float(f1_score(yt,yp,zero_division=0))}
        if prob is not None:
            try: m["roc_auc"]=float(roc_auc_score(yt,prob))
            except: m["roc_auc"]=None
        return m

    def show(n,m):
        print(f"\n--- {n} ---")
        for k,v in m.items(): print(f"  {k:10}: {'n/a' if v is None else f'{v:.4f}'}")

    results={}
    y_rule=(X_test["altitude_rate"].abs()>THRESH).astype(int)
    results["rule"]=mets(y_test,y_rule); show("Rule",results["rule"])

    qda=QuadraticDiscriminantAnalysis(); qda.fit(X_train,y_train)
    yp,pr=qda.predict(X_test), qda.predict_proba(X_test)[:,1]
    results["qda"]=mets(y_test,yp,pr); show("QDA",results["qda"])
    print(f"  CV: {cross_val_score(qda,X,y,cv=5,scoring='accuracy').mean():.4f}")

    rf=RandomForestClassifier(n_estimators=100,max_depth=12,random_state=SEED,n_jobs=-1)
    rf.fit(X_train,y_train)
    yp,pr=rf.predict(X_test), rf.predict_proba(X_test)[:,1]
    results["random_forest"]=mets(y_test,yp,pr); show("RF",results["random_forest"])

    print("\nQDA confusion:\n", confusion_matrix(y_test,qda.predict(X_test)))
    print(classification_report(y_test,qda.predict(X_test),target_names=["normal","abnormal"]))

    best_name=max([("qda",results["qda"]),("random_forest",results["random_forest"])],
                  key=lambda t:(t[1].get("f1") or 0, t[1].get("roc_auc") or 0))[0]
    best=qda if best_name=="qda" else rf
    meta={"model_name":best_name,"feature_cols":FEATURE_COLS,"metrics":results,"version":"v2-trajectories"}
    joblib.dump({"model":best,"meta":meta}, MODEL_FILE)
    json.dump(meta, open(METRICS_FILE,"w"), indent=2)
    print(f"Best={best_name} | Saved {MODEL_FILE}, {METRICS_FILE}")

if __name__=="__main__": main()