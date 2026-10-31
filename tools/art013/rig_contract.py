import struct
def read_contract(raw):
    from garrison_shared import relic_chunky as rc
    chunks=[c for c in rc.walk(rc.parse(raw).roots) if c.tag==b'SKLN']
    if len(chunks)!=1:raise ValueError('Expected one native skeleton')
    data=chunks[0].payload;offset=0
    def integer(fmt='I'):
        nonlocal offset
        value=struct.unpack_from('<'+fmt,data,offset)[0];offset+=struct.calcsize(fmt);return value
    def string():
        nonlocal offset
        size=integer()
        if not 0<size<1024 or offset+size>len(data):raise ValueError('Invalid skeleton string')
        value=data[offset:offset+size].decode('utf-8');offset+=size;return value
    version=integer();count=integer()
    if version!=0 or not 0<count<1024:raise ValueError('Unknown skeleton layout')
    bones=[{'name':string(),'parent':integer('h')} for _ in range(count)]
    reserved=integer()
    if reserved!=0:raise ValueError('Unknown post-hierarchy field')
    partitions=[{'name':string(),'start':integer(),'count':integer()} for _ in range(integer())]
    groups=[]
    for _ in range(integer()):
        name=string();slots=[integer('i') for _ in range(integer())];groups.append({'name':name,'slots':slots})
    lod_counts=[integer() for _ in range(integer())]
    if len(data)-offset!=count*40:raise ValueError('Partition parser does not end at bind block')
    return {'bones':bones,'partitions':partitions,'groups':groups,'lod_counts':lod_counts,'bind_offset':offset}
