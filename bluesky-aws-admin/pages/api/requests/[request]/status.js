import { useRouter } from 'next/router'
import { getRequestStatus } from '../../../lib/status'

// This handler fails to run when defined as an async function,
// so we're using promise then / catch syntax rather than async / await
export default (req, res) => {
    const {
        query: { request },
    } = req

    // let status = await getRequestStatus(
    //     process.env.s3.bucketName, req.query.request);
    // writeReponse(req.query.request, status);

    getRequestStatus(process.env.s3.bucketName, req.query.request)
        .then(status => {
            writeReponse(res, req.query.request, status);
        })
       .catch(err => {
            console.log("Failed to load status:" + err);
            writeReponse(res, req.query.request, null, err);
        });
}

function writeReponse(res, requestId, status, error) {
    let body = {request: requestId};
    if (status) body.status = status;
    if (error) body.error = error;
    res.statusCode = 200;
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify(body));
}
