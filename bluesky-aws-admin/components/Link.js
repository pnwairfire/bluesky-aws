// Copied and modified from:
// https://levelup.gitconnected.com/deploy-your-nextjs-application-on-a-different-base-path-i-e-not-root-1c4d210cce8a

import NextLink from 'next/link'
import { format } from 'url'
import getConfig from 'next/config'

const { publicRuntimeConfig } = getConfig()

// TODO: make sure intelligently join
//   publicRuntimeConfig.basePath and props.href/as

export default ({ children, ...props }) => {
    console.log('basePath:  ' + publicRuntimeConfig.basePath);
    console.log('href: ' +  props.href)
    console.log('as: ' +  props.as)
    return (
      <NextLink
        {...props}
        href={`${publicRuntimeConfig.basePath || ''}${format(props.href)}`}
        as={`${publicRuntimeConfig.basePath || ''}${format(props.as)}`}
      >
        {children}
      </NextLink>
    )
}
