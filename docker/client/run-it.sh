docker run -it --entrypoint "/bin/bash" \
    --volume /tmp/:/tmp/ \
    --volume /Users/ddavila/.globus/usercert.pem:/root/.globus/usercert.pem \
    --volume /Users/ddavila/.globus/userkey.pem:/root/.globus/userkey.pem \
    xrootd-client:latest
