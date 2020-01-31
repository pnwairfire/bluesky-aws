import { useRouter } from 'next/router'
import { getRunOutputFiles } from '../../../../../../lib/s3'
import { ApiServerUtils } from '../../../../../../lib/apiutils'

// This handler fails to run when defined as an async function,
// so we're using promise then / catch syntax rather than async / await
export default (req, res) => {
    const {
        query: { request, run },
    } = req

    getRunOutputFiles(process.env.fileCache.rootDir,
            process.env.s3.bucketName, req.query.request, run,
            process.env.s3.outputPath)
        .then(outputFiles => {
            ApiServerUtils.writeReponse(res, {request, run, outputFiles});
        })
       .catch(error => {
            console.log("Failed to load status:" + error);
            ApiServerUtils.writeReponse(res, {request, run, error});
        });
}
