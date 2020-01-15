// S3 Docs: https://docs.aws.amazon.com/AWSJavaScriptSDK/latest/AWS/S3.html
//var AWS = require('aws-sdk');
//var S3 = require('aws-sdk/clients/s3');
import * as AWS from 'aws-sdk';


const s3 = new AWS.S3();

// var client = s3.createClient({
//   s3Options: {
//     accessKeyId: "your s3 key",
//     secretAccessKey: "your s3 secret",
//     // any other options are passed to new AWS.S3()
//     // See: http://docs.aws.amazon.com/AWSJavaScriptSDK/latest/AWS/Config.html#constructor-property
//   },
// });



export function getRequestStatus(requestId) {
    var params = {
        Bucket: process.env.s3.bucketName,
        Key: 'status/' + requestId + '-status.json',
        Range: "bytes=0-9"
    };
    console.log('Fetching ' + params.Bucket +'/' + params.Key);
    s3.getObject(params, function(err, data) {
        if (err) {
            console.log(err); //, err.stack);
            // TODO: throw exception?
        }
        else {
            console.log(data);

           /*
           data = {
            AcceptRanges: "bytes",
            ContentLength: 10,
            ContentRange: "bytes 0-9/43",
            ContentType: "text/plain",
            ETag: "\"...\"",
            LastModified: <Date Representation>,
            Metadata: {
            },
            VersionId: "null"
           }
           */

           // TODO: return actual contentsx
           return data
        }
     });
}
