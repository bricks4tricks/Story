import re
import sys

def convert(mysql_sql):
    lines = mysql_sql.splitlines()
    result = []
    skip_patterns = (
        r'^/\\*!',
        r'^LOCK TABLES',
        r'^UNLOCK TABLES',
        r'^/\\*.*\\*/;$',
    )
    for line in lines:
        # Skip MySQL dump specific commands
        if any(re.match(p, line) for p in skip_patterns):
            continue
        line = line.replace('`', '')
        if line.strip().startswith('KEY '):
            continue
        line = re.sub(r' int NOT NULL AUTO_INCREMENT', ' SERIAL', line)
        line = line.replace('datetime', 'timestamp')
        line = line.replace('tinyint(1)', 'boolean')
        line = re.sub(r'bit\(1\) DEFAULT b\'1\'', 'boolean DEFAULT TRUE', line)
        line = re.sub(r'bit\(1\) DEFAULT b\'0\'', 'boolean DEFAULT FALSE', line)
        line = line.replace('bit(1)', 'boolean')
        # Replace MySQL binary bit values like _binary '\x01' or _binary '' with FALSE
        line = re.sub(r"_binary '[^']*'", 'FALSE', line)
        line = line.replace("NOT NULL DEFAULT '0'", 'NOT NULL DEFAULT FALSE')
        line = line.replace("NOT NULL DEFAULT '1'", 'NOT NULL DEFAULT TRUE')
        line = re.sub(r'\) ENGINE=InnoDB.*;', ');', line)
        line = line.replace('DEFAULT CHARSET=utf8mb4', '')
        line = line.replace('COLLATE=utf8mb4_0900_ai_ci', '')
        line = re.sub(r' CHARACTER SET utf8mb4', '', line)
        result.append(line)
    return '\n'.join(result)

if __name__ == '__main__':
    with open('dump.sql', 'r') as f:
        mysql_sql = f.read()
    postgres_sql = convert(mysql_sql)
    with open('dump_postgres.sql', 'w') as f:
        f.write(postgres_sql)

