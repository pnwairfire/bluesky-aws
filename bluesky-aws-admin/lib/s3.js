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

async function writeFile(fileName, dataStr) {
    let dirName = path.dirname(fileName)
    await fs.mkdir(dirName, {recursive: true})
    return await fs.writeFile(fileName, dataStr)
}


/*
 *  Listing Objects
 */

const REQUEST_INDEX_S3_PREFIX = 'request-index/';
const REQUEST_INDEX_S3_PREFIX_STRIPPER = new RegExp(
    '^' + REQUEST_INDEX_S3_PREFIX + '[0-9]{8}/');

async function listRequests(bucketName, prefix, limit, next) {
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
                requestId: e.Key.replace(REQUEST_INDEX_S3_PREFIX_STRIPPER, ''),
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

exports.getRequests = async function(bucketName, limit, next, datePrefix) {
    datePrefix = datePrefix || '';
    var prefix = REQUEST_INDEX_S3_PREFIX + datePrefix;
    return await listRequests(bucketName, prefix, limit, next);
}


/*
 *  Getting Objects
 */


// TOOD: implement cache TTL


async function getObject(bucketName, key, options) {
    options = options || {}
    let cachedFileName = (options.fileCacheRootDir
        && path.join(path.resolve(options.fileCacheRootDir), bucketName, key))
    if (options.fileCacheRootDir && await exists(cachedFileName)) {
        let contents = await fs.readFile(cachedFileName)
        return contents.base64Slice()
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
        if (options.fileCacheRootDir) {
            try {
                // TODO: don't block, since fialure to write to cache is ok
                await writeFile(cachedFileName, data)
            } catch(err) {
                console.log('Failed to write ' + key + ' to cache: ' + err)
            }
        }
        return data.base64Slice();
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
    let objStr = await getObject(bucketName, key);
    objStr = Buffer.from(objStr, 'base64').toString('ascii')
    return JSON.parse(objStr);
}

// TODO: write decorator to add file caching?

exports.getRequestInput = async function(fileCacheRootDir, bucketName, requestId) {
    let fileName = requestId + '.json'
    let key = path.join('requests', fileName);
    let objStr = await getObject(bucketName, key,
        {fileCacheRootDir: fileCacheRootDir});
    return {
        name: fileName,
        contents: objStr
    };
}

exports.getBlueskyAwsConfig = async function(fileCacheRootDir, bucketName, requestId) {
    let fileName = requestId + '-config-bluesky-aws.json'
    let key = path.join('config', fileName);
    let objStr = await getObject(bucketName, key,
        {fileCacheRootDir: fileCacheRootDir});
    objStr = Buffer.from(objStr, 'base64').toString('ascii')
    let obj = JSON.parse(objStr);
    obj.aws.iam_instance_profile.Arn = '(removed)'
    obj.aws.iam_instance_profile.Name = '(removed)'
    obj.ssh_key = '(removed)'
    obj.aws.ec2.key_pair_name = '(removed)'
    if (obj.notifications.email.username) {
        obj.notifications.email.username = '(removed)'
    }
    if (obj.notifications.email.password) {
        obj.notifications.email.password = '(removed)'
    }
    for (let i in obj.aws.ec2.security_groups) {
        obj.aws.ec2.security_groups[i] = '(removed)'
    }
    for (let i in obj.aws.ec2.efs_volumes) {
        obj.aws.ec2.efs_volumes[i][0] = '(removed)'
    }
    obj.notifications = '(removed)'
    objStr = Buffer.from(JSON.stringify(obj)).toString('base64')
    return {
        name: fileName,
        contents: objStr
    };
}

exports.getBlueskyConfig = async function(fileCacheRootDir, bucketName, requestId) {
    let fileName = requestId + '-config-bluesky.json';
    let key = path.join('config', fileName);
    let objStr = await getObject(bucketName, key,
        {fileCacheRootDir: fileCacheRootDir});
    return {
        name: fileName,
        contents: objStr
    };
}

exports.getRunLog = async function(fileCacheRootDir, bucketName, requestId, runId) {
    let fileName = runId + '.log';
    let key = path.join('log', requestId, fileName);
    let objStr = await getObject(bucketName, key,
        {fileCacheRootDir: fileCacheRootDir});
    return {
        name: fileName,
        contents: objStr
    };
}

exports.getRunInput = async function(fileCacheRootDir, bucketName, requestId, runId) {
    let fileName = runId + '-input.json'
    let key = path.join('input', requestId, fileName);
    let objStr = await getObject(bucketName, key,
        {fileCacheRootDir: fileCacheRootDir});
    return {
        name: fileName,
        contents: objStr
    };
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
