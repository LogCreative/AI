import unittest,os

from msa_dp import editDistanceDP
from msa_mdp import editDistanceMDP
from msa_ndp import editDistanceNDP
from msa_astar import editDistanceASTAR
from msa_ga import alignmentGA, costGA

S2d = ["ILOTGJJLABWTSTGGONXJMUTUXSJHKWJHCTOQHWGAGIWLZHWPKZULJTZWAKBWHXMIKLZJGLXBPAHOHVOLZWOSJJLPO", "SVSTFKPPKPNMDKLAWSWGWUUPLWHOSHHBJJIHJKSCZPKKTHUGSTKBUIFJAKKSLIKXOLCLOKWUKTTKULMJLPBLMHUVTPPJPLIZLBHJPGPGXKPJJLKH"]
ref2d = 0

S3d = ["IWTJBGTJGJTWGBJTPKHAXHAGJJSJJPPJAPJHJHJHJHJHJHJHJHJPKSTJJUWXHGPHGALKLPJTPJPGVXPLBJHHJPKWPPDJSG",
"IBLTWLIAXGWWWGKWPGWWBLAOJGAXGLOTGLJTWLXBJOQUXGOTHGXXXWOWXXMOXOPHAPPPPHAPPPHAPPPHAPPPHAATAHAAAHKXMAHAKTOHZYLP",
"HZJGGTASKJBJOGLGGWWDXZOBLKOZJXPIJPIOPXKSRHGHPHAWAOHGLIPGXLGOXGTKWPHPAMOOGPWJHBKOTXUJTKWOXPROXGUOLLMKVBGZUXKXHWPUOOIMGXX"]

ref3d = 0

class CrossTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global ref2d, ref3d
        ref2d = editDistanceMDP(S2d)[0]
        ref3d = editDistanceMDP(S3d)[0]

    def test_dp2d(self):
        dp2d = editDistanceDP(S2d[0],S2d[1])[0]
        self.assertEqual(ref2d,dp2d)

    def test_ndp2d(self):
        ndp2d = editDistanceNDP(S2d)[0][(len(S2d[0]),len(S2d[1]))]
        self.assertEqual(ref2d,ndp2d)
    
    def test_astar2d(self):
        astar2d = editDistanceASTAR(S2d)[0][(len(S2d[0]),len(S2d[1]))]
        self.assertEqual(ref2d,astar2d)

    def test_ga2d(self):
        ga2d = costGA(alignmentGA(S2d))
        self.assertGreaterEqual(ga2d, ref2d)
        self.assertLogs(str(ga2d)+"/"+str(ref2d))
    
    def test_ndp3d(self):
        ndp3d = editDistanceNDP(S3d)[0][(len(S3d[0]),len(S3d[1]),len(S3d[2]))]
        self.assertEqual(ref3d,ndp3d)
    
    def test_astar3d(self):
        astar3d = editDistanceASTAR(S3d)[0][(len(S3d[0]),len(S3d[1]),len(S3d[2]))]
        self.assertEqual(ref3d,astar3d)

    def test_ga3d(self):
        ga3d = costGA(alignmentGA(S3d))
        self.assertGreaterEqual(ga3d, ref3d)
        self.assertLogs(str(ga3d)+"/"+str(ref3d))

if __name__ == '__main__':
    unittest.main()