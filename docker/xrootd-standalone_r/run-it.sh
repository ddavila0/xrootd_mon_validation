echo "Rmember to: \ncreate xrd and copy cert/key there\ncreate ligo user\n create voms-mapfile"
docker run -it --entrypoint "/bin/bash" \
    --publish 1094:1094 \
    --volume $(pwd)/my_xrootd-standalone.cfg:/etc/xrootd/xrootd-standalone.cfg \
    --volume $(pwd)/my_auth_file:/etc/xrootd/auth_file \
    --volume $(pwd)/mygridmapfile:/etc/grid-security/grid-mapfile \
    --volume /data/:/data \
    --volume /etc/grid-security/hostcert.pem:/etc/grid-security/hostcert.pem \
    --volume /etc/grid-security/hostkey.pem:/etc/grid-security/hostkey.pem \
    --name xrootd_standalone opensciencegrid/xrootd-standalone:fresh
