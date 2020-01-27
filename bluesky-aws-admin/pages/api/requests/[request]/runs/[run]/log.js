import { useRouter } from 'next/router'
import { getRunLog } from '../../../../../../lib/status'
import { ApiServerUtils } from '../../../../../../lib/apiutils'

// This handler fails to run when defined as an async function,
// so we're using promise then / catch syntax rather than async / await
export default (req, res) => {
    const {
        query: { request, run },
    } = req

    // let status = await getRequestStatus(
    //     process.env.s3.bucketName, req.query.request);
    // ApiServerUtils.writeReponse(req.query.request, status);

    getRunLog(process.env.s3.bucketName, req.query.request, run)
        .then(log => {
            ApiServerUtils.writeReponse(res, {request, run, log});
        })
       .catch(error => {
            console.log("Failed to load status:" + error);
            ApiServerUtils.writeReponse(res, {request, run, error});
        });
}
