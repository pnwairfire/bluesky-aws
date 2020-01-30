import Alert from 'react-bootstrap/Alert'
import dynamic from 'next/dynamic';
const ReactJson=dynamic(import ('react-json-view'),{ssr:false});

import { ApiClient } from '../lib/apiutils'
import LoadingSpinner from './LoadingSpinner';
import styles from './RequestInput.module.css'

export default function RequestInput(props) {
    if (props && props.request) {
        let path ='/api/requests/' + encodeURIComponent(props.request) + '/input'
        let {data, fetchError} = ApiClient.get(path);

        let inputData = data && data.input;
        let error = fetchError || (data && data.error);
        return (
            <div className={styles['request-input']}>
                <h5>Request Input</h5>
                {!data &&
                    <LoadingSpinner />
                }
                {error &&
                    <Alert variant="danger">{error}</Alert>
                }
                {inputData &&
                    <div className={styles['json-viewer']}>
                        <ReactJson src={inputData} theme="monokai" />
                    </div>
                }
            </div>
        )
    } else {
        // need to explicitly return null so that nothing is rendered
        return null
    }
};
