// Copied and modified from:
// https://levelup.gitconnected.com/deploy-your-nextjs-application-on-a-different-base-path-i-e-not-root-1c4d210cce8a

import NextLink, { LinkProps } from 'next/link'
import { format } from 'url'
import getConfig from 'next/config'

const { publicRuntimeConfig } = getConfig()

export default ({ children, ...props }) => (
  <NextLink
    {...props}
    as={`${publicRuntimeConfig.basePath || ''}${format(props.as)}`}
  >
    {children}
  </NextLink>
)
