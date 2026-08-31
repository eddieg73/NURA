import json
import tempfile
import unittest
from pathlib import Path
import app as service

class DisplayStateTests(unittest.TestCase):
    def setUp(self):
        self.old = service.STATE_FILE
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'state.json'
        self.path.write_text(json.dumps({
            'schema_version':'1.0','generated_at':'2099-01-01T00:00:00Z','system_status':'ONLINE',
            'threat_level':'NORMAL','p0_alerts':0,'source_health':'HEALTHY','brief_status':'READY',
            'top_signal':{'title':'test','priority':'P1','confidence':'H','domain':'Cyber/Tech'},
            'watch_domains':['Cyber/Tech']
        }), encoding='utf-8')
        service.STATE_FILE = self.path
        self.client = service.app.test_client()
    def tearDown(self):
        service.STATE_FILE = self.old
        self.tmp.cleanup()
    def test_health(self):
        self.assertEqual(self.client.get('/healthz').status_code, 200)
    def test_state(self):
        r = self.client.get('/api/v1/display-state')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()['schema_version'], '1.0')

if __name__ == '__main__': unittest.main()
