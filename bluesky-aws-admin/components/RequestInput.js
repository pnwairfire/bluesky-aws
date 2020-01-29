import { ApiClient } from '../lib/apiutils'
import Alert from 'react-bootstrap/Alert'

import LoadingSpinner from './LoadingSpinner';
import styles from './RequestInput.module.css'

export default function RequestInput(props) {
    if (props && props.request) {
        let path ='/api/requests/' + props.request + '/input'
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
                    <textarea value={JSON.stringify(inputData, null, 4)} disabled />
                }
            </div>
        )
    } else {
        // need to explicitly return null so that nothing is rendered
        return null
    }
};
