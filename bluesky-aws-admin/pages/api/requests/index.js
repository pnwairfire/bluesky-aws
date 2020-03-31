// Note: as of nextjs 9.2.0, trailing slashs on urls for index APIs
//   result in 500's.  This may get fixed in 9.2.1

import { useRouter } from 'next/router'
import { getRequests } from '../../../lib/s3'
import { ApiServerUtils } from '../../../lib/apiutils'


// This handler fails to run when defined as an async function,
// so we're using promise then / catch syntax rather than async / await
export default (req, res) => {
    const {
        query: { limit, next, datePrefix },
    } = req



    getRequests(process.env.s3.bucketName,
        limit || process.env.web.requestsPaginationLimit,
        next, datePrefix)
        .then(data => {
            ApiServerUtils.writeReponse(res, data);
        })
       .catch(error => {
            console.log("Failed to get list of requests:" + error);
            ApiServerUtils.writeReponse(res, {error});
        });
}
