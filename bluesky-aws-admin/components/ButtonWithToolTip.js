import OverlayTrigger from 'react-bootstrap/OverlayTrigger'
import Tooltip from 'react-bootstrap/Tooltip'
import Button from 'react-bootstrap/Button'

export default function ButtonWithToolTip(props) {
    let title = props.title || "";
    console.log(title)
    return (
        <OverlayTrigger key={title.toLowerCase()}
            placement="top"
            overlay={
                <Tooltip>
                    {title}
                </Tooltip>
            }
        >
            <Button variant={props.variant} size="sm"
                onClick={props.onClick}
                disabled={props.disabled} >
                {props.children}
            </Button>
        </OverlayTrigger>
    )
}
