docker run -it --rm \
    --volume /tmp/:/tmp/ \
    --volume /Users/ddavila/.globus/usercert.pem:/usercert.pem \
    --volume /Users/ddavila/.globus/userkey.pem:/userkey.pem \
    --volume $(pwd)/../../utils:/utils \
    xrootd-client:latest
