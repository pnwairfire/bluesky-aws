// Note: In order to run this code from nodejs scripts without
// having to use babel-node, this code uses `require` instead of
// `import`, `exports` instead of `export`, etc.

const util = require('util');
// S3 Docs: https://docs.aws.amazon.com/AWSJavaScriptSDK/latest/AWS/S3.html
const S3 = require('aws-sdk/clients/s3');

const s3 = new S3();

const REQUEST_S3_PREFIX = 'requests/';
const REQUEST_S3_PREFIX_STRIPPER = new RegExp('^'+REQUEST_S3_PREFIX);
const JSON_EXT_STRIPPER = /.json/;


/*
 *  Listing Objects
 */

async function listObjects(bucketName, prefix) {
    let params = {
        Bucket: bucketName,
        Prefix: prefix
    };
    console.log('Fetching request ids from ' + params.Bucket);

    try {
        let data = await s3.listObjects(params).promise();
        let requests = data.Contents.map(e => {
            return {
                requestId: e.Key
                    .replace(REQUEST_S3_PREFIX_STRIPPER, '')
                    .replace(JSON_EXT_STRIPPER, ''),
                ts: e.LastModified
            }
        })
        return requests
    }
    catch (err) {
        console.log('ERROR:', err);
        throw "Failure to get request list";
    }
}

exports.getRequests = async function(bucketName) {
    return await listObjects(bucketName, REQUEST_S3_PREFIX);
}


/*
 *  Getting Objects
 */

async function getObject(bucketName, key) {
    let params = {
        Bucket: bucketName,
        Key: key
    };
    console.log('Fetching ' + params.Bucket +'/' + params.Key);

    try {
        // Note: util.promisify(s3.getObject) doesn't work with s3 sdk,
        // but s3.getObject.promise is supported
        let data = await s3.getObject(params).promise();
        return data.Body.toString();
    }
    catch (err) {
        console.log('ERROR:', err);
        if (err.code == "NoSuchKey") {
            throw key + ' does no exist';
        } else {
            throw 'Failure to load ' + key;
        }
    }
}



//export async function getRequestStatus(bucketName, requestId) {
exports.getRequestStatus = async function (bucketName, requestId) {
    let obj = await getObject(bucketName, 'status/' + requestId + '-status.json');
    return JSON.parse(obj);
}
