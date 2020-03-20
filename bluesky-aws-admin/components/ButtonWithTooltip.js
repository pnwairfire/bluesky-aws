import OverlayTrigger from 'react-bootstrap/OverlayTrigger'
import Tooltip from 'react-bootstrap/Tooltip'

function ButtonWithToolTip(props) {
    let title = props.title || "";
    console.log(title)
    return (
        <OverlayTrigger key={title.toLowerCase()}
            placement="top"
            delay={{ show: 250, hide: 250 }}
            overlay={
                <Tooltip id={"tooltip-" + title.toLowerCase()}>
                    {title}
                </Tooltip>
            }
        >
            <Button variant="outline-dark" size="sm"
                onClick={props.onClick}
                disabled={props.disabled} >
                {props.children}
            </Button>
        </OverlayTrigger>
    )
}
