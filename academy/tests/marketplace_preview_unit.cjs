const assert=require("node:assert/strict");
const {quotePreview,display}=require("../backend/marketplace-preview.js");
assert.deepEqual(quotePreview("1000.00"),{gross:1000000000n,worker:950000000n,fee:50000000n});
assert.deepEqual(quotePreview("0,01"),{gross:10000n,worker:9500n,fee:500n});
assert.equal(display(500n),"0.0005 USDC");
assert.equal(display(950000000n),"950 USDC");
assert.equal(quotePreview("1000000").gross,1000000000000n);
for(const bad of ["","0","0.00","-1","1e2","1.001","1000000.01","01"," 1","1,2.3",null,100])assert.equal(quotePreview(bad),null);
console.log("Marketplace preview arithmetic passed");
