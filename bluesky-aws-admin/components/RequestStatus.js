import Alert from 'react-bootstrap/Alert'

import LoadingSpinner from './LoadingSpinner';
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
            <h5><b>Request</b>: {props.request}</h5>
            {!props.status && (
                <LoadingSpinner />
            ) || (
                <div>
                    <div>
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
