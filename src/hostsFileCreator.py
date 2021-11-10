def create_hosts_file(ips, domain):
    hostsFileResults = []
    urlsResults = []
    counter = 1
    for ip in ips:
        hostsFileResults.append("%s *.%s.%s" % (ip, counter, domain))
        hostsFileResults.append("%s %d.%s" % (ip, counter, domain))
        counter+=1

    for i in range(1, counter):
        for j in range(1, counter):
            urlsResults.append("%d.%d.%s:8443" % (i, j, domain))

    with open('inputFiles/hostsFile', 'w') as f:
        for result in hostsFileResults:
            f.write("%s\n" % result)

    with open('inputFiles/crawlerURLs.csv', 'w') as f:
        for result in urlsResults:
            f.write("%s\n" % result)
