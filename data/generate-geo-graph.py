#############################################################################
#############################################################################
### import
from utils_flickr import *
#############################################################################
############################################################################# ### declare global parameters here
verboselevel = 1;
PARAM_outdir = "";
PARAM_minedgeDist = 0.1; #km
PARAM_maxedgeDist = 0.2; #km
#############################################################################
############################################################################# ### declare functions here
# from utils_flickr
#############################################################################
############################################################################# ### main code here
print("############ Starting ##############")
#############################################################################
verboselevel = 1;
geopics = [];
numpics = 0;

print "############ Read the list of images ##############";
totalpics = 0;
finlist = open(PARAM_outdir + 'list-images-geo.tsv', 'r');
for line in finlist:
    line = line.strip();  # rstrip, lstrip, rstrip('\n')
    id, flickrid, lat, lon, imgurl = line.split("\t");
    imagepath = PARAM_outdir + 'valid_images/' + id + '_' + flickrid + '.jpg';
    totalpics += 1;
    if(not os.path.exists(imagepath)):
        continue;
    #end
    geopics.append([id, flickrid, lat, lon, imgurl]);
    numpics += 1;
#endfor
finlist.close();

myprint("validpics=" + str(numpics) + "  totalpics=" + str(totalpics), verboselevel);

print "############ Output the list of valid images ##############";
foutlist = open(PARAM_outdir + 'valid_list-images-geo.tsv', 'w');

for i in xrange(numpics):
    id =  geopics[i][0];
    flickrid = geopics[i][1];
    lat = geopics[i][2];
    lon = geopics[i][3];
    imgurl = geopics[i][4];
    s = id + "\t" + flickrid + "\t" + lat + "\t" + lon + "\t" + imgurl + "\n";
    foutlist.write(s);
#endfor
foutlist.close();
#############################################################################
print "############ Generate graph ##############";

foutgraphcomplete = open(PARAM_outdir + 'graph-complete.tsv', 'w');
foutgraphpruned = open(PARAM_outdir + 'graph-pruned_min=' + str(PARAM_minedgeDist) + '_max=' + str(PARAM_maxedgeDist) + '.tsv', 'w');
minDistanceC = largenum;
maxDistanceC = 0;
avgDistanceC = 0;
countC = 0;
minDistanceP = largenum;
maxDistanceP = 0;
avgDistanceP = 0;
countP = 0;
for i in xrange(0,numpics):
    for j in xrange(i,numpics):
        #print i, j;
        id1 = geopics[i][0];
        flickrid1  = geopics[i][1];
        name1 = id1 + '_' + flickrid1;
        lat1 = geopics[i][2];
        lon1 = geopics[i][3];
        id2 = geopics[j][0];
        flickrid2  = geopics[j][1];
        name2 = id2 + '_' + flickrid2;
        lat2 = geopics[j][2];
        lon2 = geopics[j][3];
        distance = geoDistance(lat1, lon1, lat2, lon2);
        if(distance < minDistanceC):
            minDistanceC = distance;
        #endif
        if(distance > maxDistanceC):
            maxDistanceC = distance;
        #endif
        avgDistanceC += distance;
        countC += 1;
        s1 = name1 + "\t" + name2 + "\t" + str(distance) + "\t" + lat1 + "\t" + lon1 + "\t" + lat2 + "\t" + lon2 + "\n";
        foutgraphcomplete.write(s1);

        if((distance >= PARAM_minedgeDist) and (distance <= PARAM_maxedgeDist)):
            if(distance < minDistanceP):
                minDistanceP = distance;
            #endif
            if(distance > maxDistanceP):
                maxDistanceP = distance;
            #endif
            avgDistanceP += distance;
            countP += 1;
            s2 = name1 + "\t" + name2 + "\t" + str(distance) + "\n";
            foutgraphpruned.write(s2);
        #endif
    #endfor
#endfor
foutgraphcomplete.close();
foutgraphpruned.close();

avgDistanceC = avgDistanceC/float(countC);
myprint("minDistanceC=" + str(minDistanceC) + "  maxDistanceC=" + str(maxDistanceC) + "  avgDistanceC=" + str(avgDistanceC) + "  countC=" + str(countC), verboselevel);
avgDistanceP = avgDistanceP/float(countP);
myprint("minDistanceP=" + str(minDistanceP) + "  maxDistanceP=" + str(maxDistanceP) + "  avgDistanceP=" + str(avgDistanceP) + "  countP=" + str(countP), verboselevel);
#############################################################################
#############################################################################
print("############ Ending ##############");
#############################################################################
#############################################################################
