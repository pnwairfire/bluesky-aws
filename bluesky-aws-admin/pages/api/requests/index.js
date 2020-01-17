import { useRouter } from 'next/router'
import { getRequestStatus } from '../../../lib/status'

// This handler fails to run when defined as an async function,
// so we're using promise then / catch syntax rather than async / await
export default (req, res) => {
    getRequests(process.env.s3.bucketName)
        .then(requests => {
            writeReponse(res, requests);
        })
       .catch(err => {
            console.log("Failed to load status:" + err);
            writeReponse(res, null, err);
        });
}

function writeReponse(res, requests, error) {
    let body = {};
    if (requests) body.requests = requests;
    if (error) body.error = error;
    res.statusCode = 200;
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify(body));
}
