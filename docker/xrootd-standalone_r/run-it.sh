echo "Rmember to: \ncreate xrd and copy cert/key there\ncreate ligo user\n create voms-mapfile"
docker run -it --entrypoint "/bin/bash" \
    --publish 1094:1094 \
    --volume $(pwd)/10-my-site-variables.cfg:/etc/xrootd/config.d/10-common-site-local.cfg \
    --volume $(pwd)/my_auth_file:/etc/xrootd/auth_file \
    --volume $(pwd)/90-my-paths.cfg:/etc/xrootd/config.d/90-osg-standalone-paths.cfg \
    --volume $(pwd)/mygridmapfile:/etc/grid-security/grid-mapfile \
    --volume /tmp/to_export/:/data \
    --volume /etc/grid-security/hostcert.pem:/etc/grid-security/hostcert.pem \
    --volume /etc/grid-security/hostkey.pem:/etc/grid-security/hostkey.pem \
    opensciencegrid/xrootd-standalone:fresh
