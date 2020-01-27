import { useRouter } from 'next/router'
import { getRequestStatus } from '../../../../lib/status'
import { ApiServerUtils } from '../../../../lib/apiutils'

// This handler fails to run when defined as an async function,
// so we're using promise then / catch syntax rather than async / await
export default (req, res) => {
    const {
        query: { request },
    } = req

    // let status = await getRequestStatus(
    //     process.env.s3.bucketName, req.query.request);
    // ApiServerUtils.writeReponse(req.query.request, status);

    getRequestStatus(process.env.s3.bucketName, request)
        .then(status => {
            ApiServerUtils.writeReponse(res, {request, status});
        })
       .catch(error => {
            console.log("Failed to load status:" + error);
            ApiServerUtils.writeReponse(res, {request, error});
        });
}
