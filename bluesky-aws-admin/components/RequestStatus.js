import Alert from 'react-bootstrap/Alert'
import Spinner from 'react-bootstrap/Spinner'

import styles from './RequestStatus.module.css'


export default function RequestStatus(props) {
    let systemState = props.status && props.status.system_state;
    let systemError = !! props.status && props.status.system_error;
    let systemMessage = props.status && props.status.system_message || '(none)';

    return (
        <div className={styles['request-status']}>
            {props.error &&
                <Alert variant="danger">
                    {props.error}
                </Alert>
            }
            {props.loading && (
                <div className={styles['loading-spinner']}>
                    <Spinner animation="border" role="status" size="sm">
                    </Spinner>
                    <span>Loading...</span>
                </div>
            ) || (
                <div>
                    <div className={styles['page-section']}>
                        <div><b>Request</b>: {props.request}</div>
                        <div><b>System</b>: {systemState}</div>
                        {systemError && (
                            <Alert variant="danger">{systemError}</Alert>
                        )}
                        <div>
                            <b>Message</b>: {systemMessage}
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
