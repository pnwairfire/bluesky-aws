import { useRouter } from 'next/router'
import { getRunOutputFile } from '../../../../../../../lib/s3'
import { ApiServerUtils } from '../../../../../../../lib/apiutils'

// This handler fails to run when defined as an async function,
// so we're using promise then / catch syntax rather than async / await
export default (req, res) => {
    const {
        query: { request, run, name },
    } = req

    if (!name){
        ApiServerUtils.writeReponse(res,
            {request, run, error: "Specify 'name'"}, {statusCode: 400});
    }
    let decodedName = decodeURIComponent(name)

    getRunOutputFile(process.env.fileCache.rootDir, process.env.s3.bucketName,
            req.query.request, run, decodedName, process.env.s3.outputPath)
        .then(file => {
            ApiServerUtils.writeReponse(res, {request, run, file});
        })
       .catch(error => {
            console.log("Failed to load status:" + error);
            ApiServerUtils.writeReponse(
                res, {request, run, error}, {statusCode: 500});
        });
}
