"""BCHydro Constants"""

# Customized user agent for getting the attention of BCHydro devs
USER_AGENT = "https://github.com/emcniece/bchydro#disclaimer"

# Main login page. Several redirects follow.
URL_POST_LOGIN = "https://app.bchydro.com/sso/UI/Login"

# Goto URL that gets appended to the initial URL_POST_LOGIN request
URL_LOGIN_GOTO = "https://app.bchydro.com:443/BCHCustomerPortal/web/login.html"

URL_GET_ACCOUNTS = "https://app.bchydro.com/BCHCustomerPortal/web/getAccounts.html"
URL_ACCOUNTS_OVERVIEW = (
    "https://app.bchydro.com/BCHCustomerPortal/web/accountsOverview.html"
)

# This GET endpoint returns JSON account details.
URL_GET_ACCOUNT_JSON = "https://app.bchydro.com/evportlet/web/global-data.html"

# This consmption URL has more detail than URL_GET_USAGE but needs different form fields.
URL_POST_CONSUMPTION_XML = "https://app.bchydro.com/evportlet/web/consumption-data.html"

# Time constants in seconds
FIVE_MINUTES = 300


URL_LOGIN_PAGE = "https://app.bchydro.com/BCHCustomerPortal/web/login.html"