"""Isolated simulated treasury ledger. In-memory only; never records real revenue.
No production database, wallet connection, network or settlement side effects.
"""
import sqlite3
from datetime import datetime, timezone
from contract_lab import receipt_address
from marketplace_boundary import verify_finalized_snapshot
from marketplace_split import split

class TreasuryLab:
    def __init__(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("""CREATE TABLE receipts (
            reference TEXT PRIMARY KEY, pda TEXT UNIQUE NOT NULL,
            signature TEXT UNIQUE NOT NULL, program TEXT NOT NULL,
            payer TEXT NOT NULL, recipient TEXT NOT NULL, quote_cents INTEGER NOT NULL,
            gross INTEGER NOT NULL, worker INTEGER NOT NULL, fee INTEGER NOT NULL,
            paid_at INTEGER NOT NULL, CHECK(gross=worker+fee))""")

    def close(self):
        self.db.close()

    def record_fixture(self, invoice, program, sig, status, tx, receipt):
        if not verify_finalized_snapshot(invoice, program, sig, status, tx, receipt):
            raise ValueError("Unverified simulated payment")
        paid_at = tx["blockTime"]
        if type(paid_at) is not int or paid_at < 0:
            raise ValueError("Invalid fixture timestamp")
        datetime.fromtimestamp(paid_at, timezone.utc)
        pda, _ = receipt_address(program, invoice.payer, invoice.reference)
        a = split(invoice.quote_cents)
        row = (invoice.reference,pda,sig,program,invoice.payer,invoice.recipient,
               invoice.quote_cents,a["gross_atomic"],a["freelancer_atomic"],a["fee_atomic"],paid_at)
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            existing = self.db.execute("SELECT * FROM receipts WHERE reference=? OR pda=? OR signature=?",
                                       (invoice.reference,pda,sig)).fetchall()
            if existing:
                if existing == [row]:
                    return "already_recorded"
                raise ValueError("Conflicting simulated receipt")
            self.db.execute("INSERT INTO receipts VALUES (?,?,?,?,?,?,?,?,?,?,?)",row)
        return "recorded"

    def report(self, as_of, limit=100):
        if not isinstance(as_of,datetime) or as_of.utcoffset() is None:
            raise ValueError("Timezone required")
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError("Invalid history limit")
        now=as_of.astimezone(timezone.utc)
        end=int(now.timestamp())
        starts=[now.replace(hour=0,minute=0,second=0,microsecond=0),
                now.replace(day=1,hour=0,minute=0,second=0,microsecond=0),
                now.replace(month=1,day=1,hour=0,minute=0,second=0,microsecond=0)]
        result={}
        for name,start in zip(("day","month","year","lifetime"),starts+[None]):
            query="SELECT gross,worker,fee FROM receipts WHERE paid_at<=?"
            params=[end]
            if start is not None:
                query+=" AND paid_at>=?"
                params.append(int(start.timestamp()))
            rows=self.db.execute(query,params).fetchall()
            totals=[sum(r[i] for r in rows) for i in range(3)]
            result[name]={"count":len(rows),"gross_atomic":str(totals[0]),
                          "freelancer_atomic":str(totals[1]),"fee_atomic":str(totals[2])}
        history=self.db.execute("""SELECT reference,signature,gross,worker,fee,paid_at FROM receipts
            WHERE paid_at<=? ORDER BY paid_at DESC,reference LIMIT ?""",(end,limit)).fetchall()
        return {"simulation":True,"payment_enabled":False,"settlement_authorized":False,
                "timezone":"UTC","totals":result,"history":[{"reference":r,"signature":s,
                "gross_atomic":str(g),"freelancer_atomic":str(w),"fee_atomic":str(f),
                "paid_at":datetime.fromtimestamp(t,timezone.utc).isoformat()}
                for r,s,g,w,f,t in history]}
