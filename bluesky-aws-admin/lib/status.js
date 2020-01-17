// Note: In order to run this code from nodejs scripts without
// having to use babel-node, this code uses `require` instead of
// `import`, `exports` instead of `export`, etc.

const util = require('util');
// S3 Docs: https://docs.aws.amazon.com/AWSJavaScriptSDK/latest/AWS/S3.html
const S3 = require('aws-sdk/clients/s3');

const s3 = new S3();

//export async function getRequestStatus(bucketName, requestId) {
exports.getRequestStatus = async function (bucketName, requestId) {
    var params = {
        Bucket: bucketName,
        Key: 'status/' + requestId + '-status.json'
    };
    console.log('Fetching ' + params.Bucket +'/' + params.Key);

    try {
        // Note: util.promisify(s3.getObject) doesn't work with s3 sdk,
        // but s3.getObject.promise is supported
        var data = await s3.getObject(params).promise();
        return JSON.parse(data.Body.toString());
    }
    catch (err) {
        console.log('ERROR:', err);
        // TODO throw an exception?
    }
}
