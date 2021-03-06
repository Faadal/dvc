import os
import json

from dvc.main import main
from tests.basic_env import TestDvc


class TestMetrics(TestDvc):
    def setUp(self):
        super(TestMetrics, self).setUp()
        self.dvc.scm.commit('init')

        for branch in ['foo', 'bar', 'baz']:
            self.dvc.scm.checkout(branch, create_new=True)

            with open('metric', 'w+') as fd:
                fd.write(branch)

            with open('metric_json', 'w+') as fd:
                json.dump({'branch': branch}, fd)

            with open('metric_tsv', 'w+') as fd:
                fd.write(branch)

            with open('metric_htsv', 'w+') as fd:
                fd.write('branch\n')
                fd.write(branch)

            self.dvc.scm.add(['metric', 'metric_json', 'metric_tsv', 'metric_htsv'])
            self.dvc.scm.commit('metric')

        self.dvc.scm.checkout('master')

    def test(self):
        ret = self.dvc.metrics_show('metric', all_branches=True)
        self.assertEqual(len(ret), 3)
        self.assertTrue(ret['foo']['metric'] == 'foo')
        self.assertTrue(ret['bar']['metric'] == 'bar')
        self.assertTrue(ret['baz']['metric'] == 'baz')

        ret = self.dvc.metrics_show('metric_json', json_path='branch', all_branches=True)
        self.assertEqual(len(ret), 3)
        self.assertTrue(ret['foo']['metric_json'] == ['foo'])
        self.assertTrue(ret['bar']['metric_json'] == ['bar'])
        self.assertTrue(ret['baz']['metric_json'] == ['baz'])

        ret = self.dvc.metrics_show('metric_tsv', tsv_path='0,0', all_branches=True)
        self.assertEqual(len(ret), 3)
        self.assertTrue(ret['foo']['metric_tsv'] == ['foo'])
        self.assertTrue(ret['bar']['metric_tsv'] == ['bar'])
        self.assertTrue(ret['baz']['metric_tsv'] == ['baz'])

        ret = self.dvc.metrics_show('metric_htsv', htsv_path='branch,0', all_branches=True)
        self.assertEqual(len(ret), 3)
        self.assertTrue(ret['foo']['metric_htsv'] == ['foo'])
        self.assertTrue(ret['bar']['metric_htsv'] == ['bar'])
        self.assertTrue(ret['baz']['metric_htsv'] == ['baz'])


class TestMetricsReproCLI(TestDvc):
    def test(self):

        stage = self.dvc.run(outs_no_cache=['metrics'],
                             cmd='python {} {} {}'.format(self.CODE, self.FOO, 'metrics'))

        ret = main(['metrics', 'add', 'metrics'])
        self.assertEqual(ret, 0)

        ret = main(['repro', '-m', stage.path])
        self.assertEqual(ret, 0)

        ret = main(['metrics', 'remove', 'metrics'])
        self.assertEqual(ret, 0)

        ret = main(['repro', '-f', '-m', stage.path])
        self.assertEqual(ret, 0)


class TestMetricsCLI(TestMetrics):
    def test(self):
        #FIXME check output
        ret = main(['metrics', 'show', '--all-branches', 'metric', '-v'])
        self.assertEqual(ret, 0)

        ret = main(['metrics', 'show', '--all-branches', 'metric_json', '--json-path', 'branch'])
        self.assertEqual(ret, 0)

        ret = main(['metrics', 'show', '--all-branches', 'metric_tsv', '--tsv-path', '0,0'])
        self.assertEqual(ret, 0)

        ret = main(['metrics', 'show', '--all-branches', 'metric_htsv', '--htsv-path', 'branch,0'])
        self.assertEqual(ret, 0)
