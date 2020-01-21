

import Link from 'next/link';

import Layout from '../components/Layout'
import { getRequests } from '../lib/status'

import fetchapi from '../lib/apifetcher'



//const Index = props => {
//    let requests = props.requests;
//    let error = props.error
function Index() {
    let {data, fetchError} = fetchapi('/api/requests');

    let requests = data && data.requests;
    let error = fetchError || (data && data.error);
    console.log(data)

    return (
        <Layout>
            <div>
                {error &&
                    <Alert variant="danger">
                        error
                    </Alert>
                }
                <h4>Requests ({requests && requests.length})</h4>
                <ul>
                    {requests && requests.map((request, idx) => (
                        <li key={idx}>
                            <Link href="/requests/[id]" as={`/requests/${request.requestId}`}>
                                <a>{request.requestId} </a>
                            </Link> ({request.ts})
                        </li>
                    ))}
                </ul>
            </div>
        </Layout>
    )
};


// Index.getInitialProps = async function() {
//     // This is rendered server side, so we'l call getRequests
//     // directly rather than use the /api/requests/ api.
//     try {
//         return {
//             requests: await getRequests(process.env.s3.bucketName)
//         }
//     } catch {
//         console.log("Failed to get list of requests:" + err);
//         return {
//             error: err
//         };
//     };
// };

export default Index;
