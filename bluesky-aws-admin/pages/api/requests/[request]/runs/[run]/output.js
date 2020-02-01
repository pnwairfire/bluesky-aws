import { useRouter } from 'next/router'
import { getRunOutput } from '../../../../../../lib/s3'
import { ApiServerUtils } from '../../../../../../lib/apiutils'

// This handler fails to run when defined as an async function,
// so we're using promise then / catch syntax rather than async / await
export default (req, res) => {
    const {
        query: { request, run },
    } = req

    getRunOutput(process.env.fileCache.rootDir,
            process.env.s3.bucketName, req.query.request, run,
            process.env.s3.outputPath)
        .then(output => {
            ApiServerUtils.writeReponse(res, {request, run, output});
        })
       .catch(error => {
            console.log("Failed to load status:" + error);
            ApiServerUtils.writeReponse(res, {request, run, error}, 500);
        });
}
