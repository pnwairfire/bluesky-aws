// Note: as of nextjs 9.2.0, trailing slashs on urls for index APIs
//   result in 500's.  This may get fixed in 9.2.1

import { useRouter } from 'next/router'
import { getRequests } from '../../../lib/status'

// This handler fails to run when defined as an async function,
// so we're using promise then / catch syntax rather than async / await
export default (req, res) => {
    getRequests(process.env.s3.bucketName)
        .then(requests => {
            writeReponse(res, requests);
        })
       .catch(err => {
            console.log("Failed to get list of requests:" + err);
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
