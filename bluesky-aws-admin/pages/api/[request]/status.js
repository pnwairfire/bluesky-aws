import { useRouter } from 'next/router'
import { getRequestStatus } from '../../../lib/status'

export default (req, res) => {
    const {
        query: { request },
    } = req

    // let status = await getRequestStatus(
    //     process.env.s3.bucketName, req.query.request);
    // writeReponse(req.query.request, status);

    getRequestStatus(process.env.s3.bucketName, req.query.request)
        .then((status) => {
            writeReponse(req.query.request, status);
        })
       .catch(err => {
            console.log("The reason for the error:", );
        });
}

function writeReponse(requestId, status) {
    res.statusCode = 200
    res.setHeader('Content-Type', 'application/json')
    res.end(JSON.stringify({
        request: requestId,
        status: status
    }))
}
