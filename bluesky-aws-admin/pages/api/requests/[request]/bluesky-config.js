import { useRouter } from 'next/router'
import { getBlueskyConfig } from '../../../../lib/s3'
import { ApiServerUtils } from '../../../../lib/apiutils'

// This handler fails to run when defined as an async function,
// so we're using promise then / catch syntax rather than async / await
export default (req, res) => {
    const {
        query: { request },
    } = req

    getBlueskyConfig(process.env.fileCache.rootDir,
            process.env.s3.bucketName, request)
        .then(blueskyConfig => {
            ApiServerUtils.writeReponse(res, {request, blueskyConfig});
        })
       .catch(error => {
            console.log("Failed to load status:" + error);
            ApiServerUtils.writeReponse(
                res, {request, error}, {statusCode: 500});
        });
}
