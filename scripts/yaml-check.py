import sys
sys.path.insert(0, "/opt/data/lazy-packages")
import yaml
for f in ["/opt/data/saas-stack/docker-compose.yml",
          "/opt/data/mirth-docker-stack/docker-compose.yml",
          "/opt/data/imaging-stack/docker-compose.pacs.yml",
          "/opt/data/home/behive/docker-compose.yml",
          "/opt/data/imaging-stack/docker-compose.yml"]:
    try:
        yaml.safe_load(open(f))
        print("OK", f.split("/")[-2])
    except Exception as e:
        print("FAIL", f, str(e)[:60])
