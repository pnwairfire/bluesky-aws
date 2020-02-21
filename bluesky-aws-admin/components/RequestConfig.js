import Alert from 'react-bootstrap/Alert'
import dynamic from 'next/dynamic';
const ReactJson=dynamic(import ('react-json-view'),{ssr:false});

import { ApiClient } from '../lib/apiutils'
import LoadingSpinner from './LoadingSpinner';
import Link from './Link';
import styles from './RequestConfig.module.css'

export default function RequestConfig(props) {
    if (props && props.request) {
        let path ='/api/requests/' + encodeURIComponent(props.request) + '/bluesky-aws-config'
        let {data, fetchError} = ApiClient.get(path);

        let requestConfig = data && data.blueskyAwsConfig;
        let error = fetchError || (data && data.error);
        return (
            <div className={styles['request-config']}>
                <h5>Request Config</h5>
                {props.showFullPageLink &&
                    <Link href="/requests/[request]/config"
                            as={`/requests/${encodeURIComponent(props.request)}/config`}>
                        <a>view full page</a>
                    </Link>
                }
                {!data &&
                    <LoadingSpinner />
                }
                {error &&
                    <Alert variant="danger">{error}</Alert>
                }
                {requestConfig &&
                    <div className={styles['json-viewer']}>
                        <ReactJson src={requestConfig} theme="monokai" />
                    </div>
                }
            </div>
        )
    } else {
        // need to explicitly return null so that nothing is rendered
        return null
    }
};
