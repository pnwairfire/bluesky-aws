import Alert from 'react-bootstrap/Alert'
import dynamic from 'next/dynamic';
const ReactJson=dynamic(import ('react-json-view'),{ssr:false});

import { ApiClient } from '../lib/apiutils'
import LoadingSpinner from './LoadingSpinner';
import Link from './Link';
import styles from './ConfigViewer.module.css'

export default function ConfigViewer(props) {
    if (props && props.request) {
        let path ='/api/requests/' + encodeURIComponent(props.request) +
        '/bluesky' + (props.showRunConfig ? '' : '-aws') + '-config'
        let {data, fetchError} = ApiClient.get(path);

        let configData = data && (props.showRunConfig ? data.blueskyConfig : data.blueskyAwsConfig);
        let error = fetchError || (data && data.error);
        return (
            <div className={styles['config-viewer']}>
                <h5>{props.showRunConfig ? 'Run' : 'Request'} Config</h5>
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
                {configData &&
                    <div className={styles['json-viewer']}>
                        <ReactJson src={configData} theme="monokai" />
                    </div>
                }
            </div>
        )
    } else {
        // need to explicitly return null so that nothing is rendered
        return null
    }
};
