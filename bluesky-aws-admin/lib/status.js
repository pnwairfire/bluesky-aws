// Note: not using imports so that this script is

const util = require('util');

// S3 Docs: https://docs.aws.amazon.com/AWSJavaScriptSDK/latest/AWS/S3.html
const AWS = require('aws-sdk');
//var S3 = require('aws-sdk/clients/s3');
//import * as AWS from 'aws-sdk';

const s3 = new AWS.S3();
//const getObject = util.promisify(s3.getObject).bind;

//export async function getRequestStatus(bucketName, requestId) {
exports.getRequestStatus = async function (bucketName, requestId) {
    var params = {
        Bucket: bucketName,
        Key: 'status/' + requestId + '-status.json'
    };
    console.log('Fetching ' + params.Bucket +'/' + params.Key);

    try {
        var data = await s3.getObject(params).promise();
        return JSON.parse(data.Body.toString());
    }
    catch (err) {
        console.log('ERROR:', err);
    }
}
