//var s3 = require('s3');
//import * as s3 from 's3'

// var client = s3.createClient({
//   s3Options: {
//     accessKeyId: "your s3 key",
//     secretAccessKey: "your s3 secret",
//     // any other options are passed to new AWS.S3()
//     // See: http://docs.aws.amazon.com/AWSJavaScriptSDK/latest/AWS/Config.html#constructor-property
//   },
// });



export function getRequestStatus(requestId) {
    // var params = {
    //   localFile: "some/local/file",

    //   s3Params: {
    //     Bucket: "s3 bucket name",
    //     Key: "some/remote/file",
    //     // other options supported by getObject
    //     // See: http://docs.aws.amazon.com/AWSJavaScriptSDK/latest/AWS/S3.html#getObject-property
    //   },
    // };
    // var downloader = client.downloadFile(params);
    // downloader.on('error', function(err) {
    //   console.error("unable to download:", err.stack);
    // });
    // downloader.on('progress', function() {
    //   console.log("progress", downloader.progressAmount, downloader.progressTotal);
    // });
    // downloader.on('end', function() {
    //   console.log("done downloading");
    // });

    return { test: 'dsf'}
}
