#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按组件名称分类生成 Docsify _sidebar.md"""

import re
from pathlib import Path
from urllib.parse import quote
from collections import OrderedDict

ROOT = Path(__file__).parent
VULHUB = ROOT / "vulhub"
OUTPUT = ROOT / "_sidebar.md"

# 组件匹配规则（顺序很重要，更具体的写在前面）
RULES = [
    (r"^AJ-Report", "AJ-Report"),
    (r"^Aapche\s+Dubbo|^Apache\s+Dubbo", "Apache Dubbo"),
    (r"^Apache\s+ActiveMQ|^ActiveMQ", "Apache ActiveMQ"),
    (r"^Adminer", "Adminer"),
    (r"^Adobe\s+ColdFusion", "Adobe ColdFusion"),
    (r"^Alibaba\s+Nacos|^Nacos", "Alibaba Nacos"),
    (r"^Apache\s+APISIX", "Apache APISIX"),
    (r"^Apache\s+Airflow", "Apache Airflow"),
    (r"^Apache\s+Druid", "Apache Druid"),
    (r"^Apache\s+Flink", "Apache Flink"),
    (r"^Apache\s+HTTP|^Apache\s+HTTPD", "Apache HTTP Server"),
    (r"^Apache\s+Kafka", "Apache Kafka"),
    (r"^Apache\s+Log4j", "Apache Log4j"),
    (r"^Apache\s+OFBiz|^Apache\s+OfBiz", "Apache OFBiz"),
    (r"^Apache\s+RocketMQ", "Apache RocketMQ"),
    (r"^Apache\s+SSI", "Apache SSI"),
    (r"^Apache\s+Shiro", "Apache Shiro"),
    (r"^Apache\s+Skywalking", "Apache SkyWalking"),
    (r"^Apache\s+[Ss]olr", "Apache Solr"),
    (r"^Apache\s+Spark", "Apache Spark"),
    (r"^Apache\s+Tomcat|^Tomcat", "Apache Tomcat"),
    (r"^Apache\s+Unomi", "Apache Unomi"),
    (r"^Apereo\s+CAS", "Apereo CAS"),
    (r"^AppWeb", "AppWeb"),
    (r"^Aria2", "Aria2"),
    (r"^Atlassian\s+Confluence|^Confluence", "Atlassian Confluence"),
    (r"^Atlassian\s+Jira|^Jira", "Atlassian Jira"),
    (r"^Bash\s+", "Bash"),
    (r"^CGI\s+", "CGI"),
    (r"^CMS\s+Made\s+Simple", "CMS Made Simple"),
    (r"^Drupal", "Drupal"),
    (r"^Elasticsearch|^ElasticSearch", "Elasticsearch"),
    (r"^Flask", "Flask"),
    (r"^GhostScript|^Ghostscript", "GhostScript"),
    (r"^GitLab", "GitLab"),
    (r"^GoAhead", "GoAhead"),
    (r"^Gogs", "Gogs"),
    (r"^Grafana", "Grafana"),
    (r"^Harbor", "Harbor"),
    (r"^ImageMagick", "ImageMagick"),
    (r"^InfluxDB", "InfluxDB"),
    (r"^Jackson", "Jackson"),
    (r"^JBoss|^Jboss", "JBoss"),
    (r"^Jenkins", "Jenkins"),
    (r"^Joomla", "Joomla"),
    (r"^Jupyter", "Jupyter"),
    (r"^Kibana", "Kibana"),
    (r"^Laravel", "Laravel"),
    (r"^MySQL", "MySQL"),
    (r"^Nginx", "Nginx"),
    (r"^Node\.?js|^Node\s", "Node.js"),
    (r"^OpenSSH|^OpenSSL", "OpenSSH/OpenSSL"),
    (r"^PHP\s", "PHP"),
    (r"^PostgreSQL", "PostgreSQL"),
    (r"^RabbitMQ", "RabbitMQ"),
    (r"^Redis", "Redis"),
    (r"^Ruby\s+on\s+Rails|^Rails", "Ruby on Rails"),
    (r"^Samba", "Samba"),
    (r"^Saltstack|^SaltStack", "SaltStack"),
    (r"^ShowDoc", "ShowDoc"),
    (r"^SonarQube", "SonarQube"),
    (r"^Spring", "Spring"),
    (r"^Struts2", "Struts2"),
    (r"^Supervisord|^Supervisor", "Supervisord"),
    (r"^ThinkPHP", "ThinkPHP"),
    (r"^Tiki\s+Wiki", "Tiki Wiki"),
    (r"^V2board", "V2board"),
    (r"^Weblogic|^WebLogic", "WebLogic"),
    (r"^Webmin", "Webmin"),
    (r"^WebSphere", "WebSphere"),
    (r"^Wordpress|^WordPress", "WordPress"),
    (r"^XDebug", "XDebug"),
    (r"^XStream", "XStream"),
    (r"^XXL-JOB|^XXL.?JOB", "XXL-JOB"),
    (r"^YApi", "YApi"),
    (r"^Zabbix|^zabbix", "Zabbix"),
    (r"^docker\s+", "Docker"),
    (r"^elFinder", "elFinder"),
    (r"^electron", "Electron"),
    (r"^fastjson", "Fastjson"),
    (r"^ffmpeg", "FFmpeg"),
    (r"^gitlist", "Gitlist"),
    (r"^kkFileView", "kkFileView"),
    (r"^librsvg", "librsvg"),
    (r"^libssh", "libssh"),
    (r"^mini_httpd", "mini_httpd"),
    (r"^mongo-express", "mongo-express"),
    (r"^node-postgres", "node-postgres"),
    (r"^ntopng", "ntopng"),
    (r"^pgAdmin", "pgAdmin"),
    (r"^phpMyAdmin|^phpmyadmin", "phpMyAdmin"),
    (r"^phpunit", "PHPUnit"),
    (r"^rsync", "rsync"),
    (r"^scrapyd", "Scrapyd"),
    (r"^uWSGI", "uWSGI"),
]


def get_component(filename: str) -> str:
    name = filename.replace(".md", "").replace("Aapche", "Apache")
    for pattern, comp in RULES:
        if re.search(pattern, name, re.I):
            return comp
    # 兜底：取第一个词
    first = re.split(r"[\s（(]", name)[0]
    return first or "其他"


def encode_path(path: str) -> str:
    return "/".join(quote(part) for part in path.split("/"))


def main():
    if not VULHUB.exists():
        print(f"❌ 找不到目录: {VULHUB}")
        return

    files = sorted(VULHUB.glob("*.md"), key=lambda p: p.name.lower())
    groups = OrderedDict()

    for f in files:
        comp = get_component(f.name)
        groups.setdefault(comp, []).append(f)

    # 按组件名排序
    lines = ["* [首页](README.md)", ""]
    for comp in sorted(groups.keys(), key=str.lower):
        lines.append(f"* **{comp}**")
        for f in groups[comp]:
            title = f.stem
            rel = f.relative_to(ROOT).as_posix()
            lines.append(f"  * [{title}]({encode_path(rel)})")
        lines.append("")

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ 已生成 {OUTPUT}")
    print(f"   笔记总数: {len(files)}")
    print(f"   组件分类: {len(groups)}")
    print("\n分类统计:")
    for comp in sorted(groups.keys(), key=str.lower):
        print(f"   {comp}: {len(groups[comp])} 篇")


if __name__ == "__main__":
    main()
