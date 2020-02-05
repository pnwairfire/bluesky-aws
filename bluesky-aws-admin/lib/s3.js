// Note: In order to run this code from nodejs scripts without
// having to use babel-node, this code uses `require` instead of
// `import`, `exports` instead of `export`, etc.

const fs = require('fs').promises;
const util = require('util');
const path = require('path');
const exec = util.promisify(require('child_process').exec);
const exists = util.promisify(require('fs').exists)

// S3 Docs: https://docs.aws.amazon.com/AWSJavaScriptSDK/latest/AWS/S3.html
const S3 = require('aws-sdk/clients/s3');

const fileutils = require('./fileutils')

const s3 = new S3();

const REQUEST_S3_PREFIX = 'requests/';
const REQUEST_S3_PREFIX_STRIPPER = new RegExp('^'+REQUEST_S3_PREFIX);
const JSON_EXT_STRIPPER = /.json/;

async function writeFile(filename, dataStr) {
    let dirName = path.dirname(filename)
    await fs.mkdir(dirName, {recursive: true})
    return await fs.writeFile(filename, dataStr)
}


/*
 *  Listing Objects
 */

async function listObjects(bucketName, prefix, limit, next) {
    let params = {
        Bucket: bucketName,
        Prefix: prefix,
        ContinuationToken: next,
        MaxKeys: limit || 25
    };

    console.log('Fetching request ids from ' + params.Bucket);

    try {
        let data = await s3.listObjectsV2(params).promise();
        let requests = data.Contents.map(e => {
            return {
                requestId: e.Key
                    .replace(REQUEST_S3_PREFIX_STRIPPER, '')
                    .replace(JSON_EXT_STRIPPER, ''),
                ts: e.LastModified
            }
        })
        return {requests, next: data.NextContinuationToken}
    }
    catch (err) {
        console.log('ERROR:', err);
        throw 'Failure to get request list: ' + err.message;
    }
}

exports.getRequests = async function(bucketName, limit, next) {
    return await listObjects(bucketName, REQUEST_S3_PREFIX, limit, next);
}


/*
 *  Getting Objects
 */


// TOOD: implement cache TTL


async function getObject(bucketName, key, options) {
    options = options || {}
    let cachedFileName = (options.fileCacheRootDir
        && path.join(options.fileCacheRootDir, bucketName, key))

    if (options.fileCacheRootDir && await exists(cachedFileName)) {
        let contents = await fs.readFile(cachedFileName)
        if (options.convertToString) contents = contents.toString();
        return contents
    }

    let params = {
        Bucket: bucketName,
        Key: key
    };
    console.log('Fetching ' + params.Bucket +'/' + params.Key);

    try {
        // Note: util.promisify(s3.getObject) doesn't work with s3 sdk,
        // but s3.getObject.promise is supported
        let data = (await s3.getObject(params).promise());
        data = data.Body
        if (options.convertToString) data = data.toString();
        if (options.fileCacheRootDir) {
            try {
                // TODO: don't block, since fialure to write to cache is ok
                await writeFile(cachedFileName, data)
            } catch(err) {
                console.log('Failed to write ' + key + ' to cache')
            }
        }
        return data;
    }
    catch (err) {
        console.log('ERROR:', err);
        if (err.code == 'NoSuchKey') {
            throw key + ' does no exist';
        } else {
            throw 'Failure to load ' + key;
        }
    }
}

//export async function getRequestStatus(bucketName, requestId) {
exports.getRequestStatus = async function(bucketName, requestId) {
    // Note: we don't cache request status
    let key = path.join('status',requestId + '-status.json');
    let objStr = await getObject(bucketName, key, {convertToString: true});
    return JSON.parse(objStr);
}

// TODO: write decorator to add file caching?

exports.getRequestInput = async function(fileCacheRootDir, bucketName, requestId) {
    let key = path.join('requests', requestId + '.json');
    let objStr = await getObject(bucketName, key,
        {fileCacheRootDir: fileCacheRootDir, convertToString: true});
    return JSON.parse(objStr);
}

exports.getRunLog = async function(fileCacheRootDir, bucketName, requestId, runId) {
    let key = path.join('log', requestId, runId + '.log');
    return await getObject(bucketName, key,
        {fileCacheRootDir: fileCacheRootDir, convertToString: true});
}

async function downloadOutput(
        fileCacheRootDir, bucketName, requestId, runId, outputPath) {
    let keyBase = path.join(outputPath, requestId, runId);
    let key = keyBase + '.tar.gz';
    // we'll ignore objStr (unless we switch to a npm tar package
    // and untar/zip in memory)
    let objStr = await getObject(bucketName, key,
        {fileCacheRootDir: fileCacheRootDir});
    let unpackedRootDir = path.join(fileCacheRootDir, bucketName, keyBase)
    if (!await exists(unpackedRootDir)) {
        // TODO: use fs-tar, tar-stream, or tar npm packages ???
        let cwd = path.join(fileCacheRootDir, bucketName, outputPath, requestId);
        let cmd = 'tar xzf ' + runId + '.tar.gz'
        await exec(cmd, {cwd: cwd});
    }
    if (!await exists(unpackedRootDir)) {
        throw "Failed to fetch output file " + key
    }

    return unpackedRootDir;
}

exports.getRunOutputFiles = async function(fileCacheRootDir,
        bucketName, requestId, runId, outputPath) {
    unpackedRootDir = await downloadOutput(fileCacheRootDir,
        bucketName, requestId, runId, outputPath);

    return fileutils.listFiles(unpackedRootDir);
}

exports.getRunOutputFile = async function(fileCacheRootDir,
        bucketName, requestId, runId, filepath, outputPath) {
    unpackedRootDir = await downloadOutput(fileCacheRootDir,
        bucketName, requestId, runId, outputPath);

    filepath = path.join(unpackedRootDir, filepath)
    return await fileutils.getFile(filepath);
}
