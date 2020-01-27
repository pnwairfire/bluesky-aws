import { ApiClient } from '../lib/apiutils'
import Alert from 'react-bootstrap/Table'

import styles from './RequestInput.module.css'

export default function RequestInput(props) {
    let path ='/api/requests/' + props.request + '/input'
    let {data, fetchError} = ApiClient.get(path);

    let inputData = data && data.input;
    let error = fetchError || (data && data.error);

    return (
        <div>
            <h5>Request Input</h5>
            {error &&
                <Alert variant="danger">{error}</Alert>
            }
            {inputData &&
                <textarea className={styles.requestinput} value={JSON.stringify(inputData, null, 4)} disabled />
            }
        </div>
    )
};
