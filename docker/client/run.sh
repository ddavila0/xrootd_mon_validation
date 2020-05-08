docker run --rm \
    --volume /tmp/:/tmp/ \
    --volume /Users/ddavila/.globus/usercert.pem:/usercert.pem \
    --volume /Users/ddavila/.globus/userkey.pem:/userkey.pem \
    xrootd_client:latest
