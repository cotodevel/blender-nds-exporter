#!BPY
"""
    Nintendo DS CallList Exporter for Blender
    Copyright © 2008, 2009 Kevin Roy <kiniou_AT_gmail_DOT_com>

    Nintendo DS CallList Exporter for Blender is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

""" Registration info for Blender menus:
Name: 'Nintendo DS CallList'
Blender: 246
Group: 'Export'
Tip: 'Export for Nintendo DS'
"""
__author__ = "Kevin (KiNiOu) ROY"
__url__ = ("blender", "kiniou", "Author's site, http://blog.knokorpo.fr")
__version__ = "0.2"

__bpydoc__ = """\
This script export models in Nintendo DS CallList for
the DevKitPro SDK in a .h file.

Usage:
Go to Export and type a name for the file.
"""

import struct
import array

import bpy
import random
import math

# Define libnds binary functions and macros

def floattov16(n) :
    #return array.array(n * (1<<12) , Float32).astype(Int16)
    return int( n * (1<<12) )

def VERTEX_PACK(x,y) :
    #return array.array((x & 0xFFFF) | (y << 16) , Int32)
    return ( (x & 0xFFFF) | (y << 16) )

def floattov10(n) :
    if (n>.998) :
        #return array.array(0x1FF , Int16)
        return ( 0x1FF )
    else :
        #return array.array(n * (1<<9) , Float32).astype(Int16)
        return int( n * (1<<9) ) 

def NORMAL_PACK(x,y,z) :
    #return array.array((x & 0x3FF) | ((y & 0x3FF) << 10) | (z << 20) , Int32)
    return ( (x & 0x3FF) | ((y & 0x3FF) << 10) | (z << 20) )

def floattot16(n) :
    #return array.array( n * (1 << 4) , Float32).astype(Int16)
    return int( n * (1 << 4) )

def TEXTURE_PACK(u,v) :
    #return array.array( (u & 0xFFFF) | (v << 16) , Int32)
    return ( (u & 0xFFFF) | (v << 16) )

def RGB15(r,g,b) :
    #return array.array(r | (g << 5) | (b <<10 ) , Int32)
    return ( r | (g << 5) | (b <<10 ) )

FIFO_VERTEX16  = 0x23
FIFO_NORMAL    = 0x21
FIFO_TEX_COORD = 0x22
FIFO_COLOR     = 0x20
FIFO_NOP       = 0x00
FIFO_BEGIN     = 0x40
FIFO_END       = 0x41

GL_GLBEGIN_ENUM = {
    'GL_TRIANGLES'      : 0 ,
    'GL_QUADS'          : 1 ,
    'GL_TRIANGLE_STRIP' : 2 ,
    'GL_QUAD_STRIP'     : 3 ,
    'GL_TRIANGLE'       : 0 ,
    'GL_QUAD'           : 1
}

EXPORT_OPTIONS = {
    'FORMAT_TEXT'   : 1,
    'FORMAT_BINARY' : 0,
    'TEXCOORDS'     : 1,
    'NO_TEXCOORDS'  : 0,
    'COLORS'        : 1,
    'NO_COLORS'     : 0,
    'NORMALS'       : 1,
    'NO_NORMALS'    : 0
}

# a _mesh_option represents export options in the gui
class _mesh_options (object) :
    __slots__ = 'format' , 'uv_export' ,'texfile_export' , 'normals_export' , 'color_export' , 'mesh_data' , 'mesh_name', 'texture_data' , 'texture_list' , 'texture_w' , 'texture_h', 'dir_path'

    def __init__(self,mesh_data,dir_path) :
        self.format         = EXPORT_OPTIONS['FORMAT_TEXT']   #Which format for the export? FORMAT_BINARY->Binary, FORMAT_TEXT->C-Style
        self.uv_export      = EXPORT_OPTIONS['TEXCOORDS']    #Do we export uv coordinates? NO_TEXCOORDS->No, TEXCOORDS->Yes
        self.normals_export = EXPORT_OPTIONS['NORMALS']         #Do we export normals coordinates ? NO_NORMALS->No, NORMALS->Yes
        self.color_export   = EXPORT_OPTIONS['NO_COLORS']          #Do we export color attributes ? COLORS->No, NO_COLORS->Yes

        self.mesh_data = mesh_data #The Blender Mesh data
        self.mesh_name = mesh_data.name #The Blender Mesh name
        self.texture_w = 0
        self.texture_h = 0
        self.list_textures() #Retrieve all texture bound to the Blender mesh
#        print(self.mesh_data)
#        print(self.mesh_data.uv_textures)
#        print(dir(self.mesh_data))
        
        if (self.mesh_data.active_uv_texture ): self.uv_export = EXPORT_OPTIONS['TEXCOORDS']
        else: self.uv_export = EXPORT_OPTIONS['NO_TEXCOORDS']
        if (self.mesh_data.vertex_colors ) : self.color_export = EXPORT_OPTIONS['COLORS']
        else: self.color_export = EXPORT_OPTIONS['NO_COLORS']
        
        self.dir_path = dir_path
        self.texfile_export = 0
        

    def list_textures(self) :
        print("listing textures for mesh \"%s\"" % self.mesh_name)
        materials = self.mesh_data.materials
        self.texture_data = []
        #Here we take the first material in the mesh
        tex = []
        if len(materials)>0 :
            tex = materials[0].textures

        self.texture_list = []
        #Here we take the first Texture of Image Type
        img_found = 0
        if len(tex)>0 :
            for t in tex :
                if t != None :
                    if (type(t.texture) == bpy.types.ImageTexture and t.texture.image != None) :
                        image = t.texture.image
                        self.texture_list.append(t)
                        #TODO : When image size will be accessible
                        #img_found = 1

                        #print "%s %dx%d" % (image.getName(),image.getSize()[0],image.getSize()[1])

        if (img_found == 1):
            print(dir(image))
            print(image.display_aspect)
            image = self.texture_list[0].texture.image
            self.texture_data.append(image)

            w = 0
            h = 0
#            w = image.getSize()[0]
#            h = image.getSize()[1]
#            ratio = float(w)/float(h)
#            print("Texture %s %dx%d ratio=%f" % (image.name,w,h,ratio))

            if (w > 128) : w = 128
            if (w < 8) : w = 8

            if (h > 128) : h = 128
            if (h < 8) : h = 8

            if (ratio < 1.0) :
                w = h * (1/round(1/ratio))
                print("ratio <  1 : Texture %s %dx%d" % (image.getName(),w,h))
            else :
                h = w / round(ratio)
                print("ratio >= 1 :Texture %s %dx%d" % (image.getName(),w,h))

            self.texture_w = int(w)
            self.texture_h = int(h)
        else :
            print("!!!Warning : Cannot find any textures bound to the mesh!!!")
            print("!!!          TEXTURE_PACKs won't be exported           !!!")

    def get_final_path_mesh(self):
        return ("%s%s%s" % ( self.dir_path,self.mesh_name , (".h" if (self.format) else ".bin") ) )
#        return ( Blender.sys.join(self.dir_path,self.mesh_name + (".h" if (self.format) else ".bin")) )

    def get_final_path_tex(self):
        return( "%s%s%s" % (self.dir_path , self.mesh_name , ".pcx") )
#        return ( Blender.sys.join(self.dir_path,self.mesh_name + ".pcx") )

    def __str__(self):
        return "File Format:%s , Exporting Texture:%s , Exporting Normals:%s , Exporting Colors:%s" % (self.format,self.uv_export,self.normals_export,self.color_export)


class _nds_cmdpack_nop(object) :
    __slots__ = 'cmd','val'

    def __init__(self):
        self.cmd = {}
        self.cmd[EXPORT_OPTIONS['FORMAT_TEXT']] = "FIFO_NOP"
        self.cmd[EXPORT_OPTIONS['FORMAT_BINARY']] = struct.pack( 'b' , FIFO_NOP )


        self.val = {}
        self.val[EXPORT_OPTIONS['FORMAT_TEXT']] = None
        self.val[EXPORT_OPTIONS['FORMAT_BINARY']] = None

    def get_cmd(self,format):
        return ( self.cmd[format] )

    def get_val(self,format):
        return ( self.val[format] )

    def get_nb_val(self):
        return ( 0 )

    def __str__(self):
        return ( "%s , %s" % ( self.cmd[EXPORT_OPTIONS['FORMAT_TEXT']], self.val[EXPORT_OPTIONS['FORMAT_TEXT']]) )

class _nds_cmdpack_begin (object) :
    __slots__ = 'cmd','val'

    def __init__(self,begin_opt):
        self.cmd = {}
        self.cmd[EXPORT_OPTIONS['FORMAT_TEXT']] = "FIFO_BEGIN"
        self.cmd[EXPORT_OPTIONS['FORMAT_BINARY']] = struct.pack( 'b' , FIFO_BEGIN )


        self.val = {}
        self.val[EXPORT_OPTIONS['FORMAT_TEXT']] = begin_opt
        self.val[EXPORT_OPTIONS['FORMAT_BINARY']] = struct.pack('<i' , GL_GLBEGIN_ENUM[begin_opt] )


    def get_cmd(self,format):
        return ( self.cmd[format] )

    def get_val(self,format):
        return ( self.val[format] )

    def get_nb_val(self):
        return ( 1 )

    def __str__(self):
        return ( "%s , %s" % ( self.cmd[EXPORT_OPTIONS['FORMAT_TEXT']], self.val[EXPORT_OPTIONS['FORMAT_TEXT']]) )

class _nds_cmdpack_end(object) :

    __slots__ = 'cmd','val'

    def __init__(self):
        self.cmd = {}
        self.cmd[EXPORT_OPTIONS['FORMAT_TEXT']] = "FIFO_END"
        self.cmd[EXPORT_OPTIONS['FORMAT_BINARY']] = struct.pack( 'b' , FIFO_END )


        self.val = {}
        self.val[EXPORT_OPTIONS['FORMAT_TEXT']] = None
        self.val[EXPORT_OPTIONS['FORMAT_BINARY']] = None


    def get_cmd(self,format):
        return ( self.cmd[format] )

    def get_val(self,format):
        return ( self.val[format] )

    def get_nb_val(self):
        return ( 0 )

    def __str__(self):
        return ( "%s , %s" % ( self.cmd[EXPORT_OPTIONS['FORMAT_TEXT']], self.val[EXPORT_OPTIONS['FORMAT_TEXT']]) )


class _nds_cmdpack_vertex (object) :
    __slots__ = 'cmd','val'

    def __init__(self,vertex=(0.0,0.0,0.0)):
        x, y, z = vertex
        self.cmd = {}
        self.cmd[EXPORT_OPTIONS['FORMAT_TEXT']] = "FIFO_VERTEX16"
        self.cmd[EXPORT_OPTIONS['FORMAT_BINARY']] = struct.pack( 'b' , FIFO_VERTEX16 )


        self.val = {}
        self.val[EXPORT_OPTIONS['FORMAT_TEXT']] = "VERTEX_PACK(floattov16(%f),floattov16(%f)) , VERTEX_PACK(floattov16(%f),0)" % (x,y,z)
        self.val[EXPORT_OPTIONS['FORMAT_BINARY']] = struct.pack('<ii' , VERTEX_PACK(floattov16(x) , floattov16(y)) , VERTEX_PACK(floattov16(z) , 0))


    def get_cmd(self, format):
        return ( self.cmd[format] )

    def get_val(self, format):
        return ( self.val[format] )

    def get_nb_val(self):
        return ( 2 )

    def __str__(self):
        return ( "%s , %s" % ( self.cmd[EXPORT_OPTIONS['FORMAT_TEXT']], self.val[EXPORT_OPTIONS['FORMAT_TEXT']]) )


class _nds_cmdpack_normal (object):
    __slots__ = 'cmd','val'

    def __init__(self,normal=(0.0,0.0,0.0)):
        x, y, z = normal
        self.cmd = {}
        self.cmd[EXPORT_OPTIONS['FORMAT_TEXT']] = "FIFO_NORMAL"
        self.cmd[EXPORT_OPTIONS['FORMAT_BINARY']] = struct.pack( 'b' , FIFO_NORMAL )


        self.val = {}
        self.val[EXPORT_OPTIONS['FORMAT_TEXT']] =  "NORMAL_PACK(floattov10(%3.6f),floattov10(%3.6f),floattov10(%3.6f))" % (x,y,z)
        self.val[EXPORT_OPTIONS['FORMAT_BINARY']] = struct.pack('<i' , NORMAL_PACK(floattov10(x) , floattov10(y) , floattov10(z)))


    def get_cmd(self, format):
        return ( self.cmd[format] )

    def get_val(self, format):
        return ( self.val[format] )

    def get_nb_val(self):
        return ( 1 )

    def __str__(self):
        return ( "%s , %s" % ( self.cmd[EXPORT_OPTIONS['FORMAT_TEXT']], self.val[EXPORT_OPTIONS['FORMAT_TEXT']]) )

class _nds_cmdpack_color (object):
    __slots__ = 'cmd' , 'val'

    def __init__(self,color=(0,0,0)):
        r,g,b = color
        self.cmd = {}
        self.cmd[EXPORT_OPTIONS['FORMAT_TEXT']] = "FIFO_COLOR"
        self.cmd[EXPORT_OPTIONS['FORMAT_BINARY']] = struct.pack( 'b' , FIFO_COLOR )


        self.val = {}
        self.val[EXPORT_OPTIONS['FORMAT_TEXT']] =  "RGB15(%d,%d,%d)" % (r,g,b)
        self.val[EXPORT_OPTIONS['FORMAT_BINARY']] = struct.pack( '<i' , RGB15(r,g,b) )


    def get_cmd(self, format):
        return ( self.cmd[format] )

    def get_val(self, format):
        return ( self.val[format] )

    def get_nb_val(self):
        return ( 1 )

    def __str__(self):
        return ( "%s , %s" % ( self.cmd[EXPORT_OPTIONS['FORMAT_TEXT']], self.val[EXPORT_OPTIONS['FORMAT_TEXT']]) )


class _nds_cmdpack_texture (object):
    __slots__ = 'cmd' , 'val'

    def __init__(self,uv=(0.0,0.0)):
        u,v = uv
        self.cmd = {}
        self.cmd[EXPORT_OPTIONS['FORMAT_TEXT']] = "FIFO_TEX_COORD"
        self.cmd[EXPORT_OPTIONS['FORMAT_BINARY']] = struct.pack( 'b' , FIFO_TEX_COORD )


        self.val = {}
        self.val[EXPORT_OPTIONS['FORMAT_TEXT']] =  "TEXTURE_PACK(floattot16(%3.6f),floattot16(%3.6f))" % (u,v)
        self.val[EXPORT_OPTIONS['FORMAT_BINARY']] = struct.pack( '<i' , TEXTURE_PACK( floattot16(u) , floattot16(v) ) )


    def get_cmd(self, format):
        return ( self.cmd[format] )

    def get_val(self, format):
        return ( self.val[format] )

    def get_nb_val(self):
        return ( 1 )

    def __str__(self):
        return ( "%s , %s" % ( self.cmd[EXPORT_OPTIONS['FORMAT_TEXT']], self.val[EXPORT_OPTIONS['FORMAT_TEXT']]) )


class _nds_mesh_vertex (object):
    __slots__ = 'vertex','uv','normal','color'

    def __init__(self):
        self.vertex = None
        self.uv = None
        self.normal = None
        self.color = None

    def __str__(self):
        return "MESH_VERTEX(vertex=%s uv=%s normal=%s color=%s)" % (self.vertex , self.uv , self.normal , self.color)


class _nds_cmdpack (object) :
    __slots__ = 'commands'

    def __init__(self):
        self.commands = []

    def add(self, cmd):
        if self.len() == 4:
            return ( False )
        else :
            self.commands.append(cmd)
            return ( True )

    def terminate(self):
        if (self.len() < 4):
            for i in range(self.len(),4):
                self.commands.append(_nds_cmdpack_nop())

    def len(self):
        return ( len(self.commands) )

    def get_nb_param(self):
        if self.len() == 0:
            return ( 0 )
        else :
            nb = 1

        for i in self.commands:
            nb += i.get_nb_val()

        return ( nb )

    def get_pack(self,format):
        if ( format == EXPORT_OPTIONS['FORMAT_TEXT'] ) :
            str = ""
        else :
            str = []
        str += self.get_cmd(format)
        str += self.get_val(format)
        return ( str )

    def get_cmd(self,format):
        c = self.commands
        if ( format == EXPORT_OPTIONS['FORMAT_TEXT'] ) :
            cmd = ""
            cmd += "FIFO_COMMAND_PACK( %s , %s , %s , %s ),\n" % ( c[0].get_cmd(format) ,c[1].get_cmd(format) ,c[2].get_cmd(format) ,c[3].get_cmd(format) )
        elif ( format == EXPORT_OPTIONS['FORMAT_BINARY'] ) :
            cmd = []
            cmd += c[0].get_cmd(format) + c[1].get_cmd(format) + c[2].get_cmd(format) + c[3].get_cmd(format)
        return cmd

    def get_val(self,format):
        if ( format == EXPORT_OPTIONS['FORMAT_TEXT'] ) :
            val = ""
            for i in self.commands:
                if ( i.get_val(format) != None ):
                    val += i.get_val(format)
                    val += ",\n"
        else:
            val = []
            for i in self.commands:
                if ( i.get_val(format) != None ):
                    val += i.get_val(format)

        return val

    def __str__(self):
        str = "CMD_PACK ELEMENT:\n"
        for i in self.commands:
            str += "%s\n" % (i)
        return ( str )



class _nds_cmdpack_list (object):
    __slots__ = 'list'

    def __init__(self):
        self.list = [ _nds_cmdpack() ]

    def add(self,cmd):
        if ( self.list[-1].add(cmd) == False ):
            self.list.append( _nds_cmdpack() )
            self.list[-1].add(cmd)

    def len(self):
        return ( len(self.list) )

    def get_nb_params(self):
        nb = 0
        for i in self.list :
            nb += i.get_nb_param()

        return ( nb )

    def terminate(self):
        self.list[-1].terminate()

    def get_pack(self,format):
        if (format == EXPORT_OPTIONS['FORMAT_TEXT']) :
            str = ""
        else :
            str = []

        for cp in self.list:
            str += cp.get_pack(format)
                
        return ( str )

    def __str__(self):
        str = "COMMAND_PACK LIST\n"
        for i in self.list :
            str += "%s\n" % ( i )
        return ( str )


class _nds_mesh (object) :
    __slots__ = 'name', 'quads' , 'triangles' , 'texture' , 'cmdpack_list' , 'cmdpack_count' , 'options', 'final_cmdpack'


    def __init__(self,mesh_options):
        print( mesh_options )
        self.options = mesh_options
        self.quads = []
        self.triangles = []
        self.cmdpack_list = _nds_cmdpack_list()
#        print( self.cmdpack_list )
        self.cmdpack_count = 0
        

        self.name = mesh_options.mesh_name
        self.get_faces(mesh_options.mesh_data)
        #self.rescale_mesh(mesh_options.mesh_data)

        self.prepare_cmdpack()
#        print( self.cmdpack_list)
        self.construct_cmdpack()

    def save_tex(self) :
        try:
            import PIL.Image
        except ImportError :
            print( "Python Imaging Library not installed" )
        else :
            print( self.options.texture_data[0].filename )
#            print( Blender.sys.expandpath(self.options.texture_data[0].filename) )
            if (self.options.texture_data[0].packed ) : self.options.texture_data[0].unpack(Blender.UnpackModes.USE_LOCAL)
            img = PIL.Image.open(Blender.sys.expandpath(self.options.texture_data[0].getFilename()))
            img_rgb = img.convert("RGB")
            img_pal = img_rgb.convert("P",palette=PIL.Image.ADAPTIVE)
            img_res = img_pal.resize((self.options.texture_w,self.options.texture_h) )
            img_res.save(self.options.get_final_path_tex())


    def add_nds_mesh_vertex(self,blender_mesh , face,face_list):
        for n,i in enumerate(face.verts):
            nds_mesh_vertex = _nds_mesh_vertex()
            #we copy vertex's coordinates information
            nds_mesh_vertex.vertex = _nds_cmdpack_vertex(blender_mesh.verts[i].co)
            #we copy vertex's normals information
            nds_mesh_vertex.normal = _nds_cmdpack_normal(blender_mesh.verts[i].normal)
            #we copy vertex's UV coordinates information only if there is UV layer for the current mesh
            if (self.options.uv_export) :
                uv = blender_mesh.active_uv_texture.data[face.index].uv[n]
                
#                for n,ut in enumerate(blender_mesh.active_uv_texture.data) :
#                    for u in ut.uv : print(n,float(u[0]), float(u[1]))
#                if (face.uv[i].x >= 0 and face.uv[i].y >= 0):
                #nds_mesh_vertex.uv = _nds_cmdpack_texture( ( face.uv[i].x * self.options.texture_w , (1-face.uv[i].y) * self.options.texture_h))
                nds_mesh_vertex.uv = _nds_cmdpack_texture( ( uv[0] , (1-uv[1])))
            #we copy vertex's color only if there is Color Layer for the current mesh
            if (self.options.color_export) :
                nds_mesh_vertex.color = _nds_cmdpack_color( (face.col[i].r * 32 / 256 , face.col[i].g * 32 / 256, face.col[i].b * 32 / 256) )
            #finally, we append the nds_mesh_vertex in the quads list
            face_list.append(nds_mesh_vertex)

    def get_faces(self,blender_mesh):
        for face in blender_mesh.faces :
            #we process the face only if this is a quad
            if (len(face.verts) == 4) :
                self.add_nds_mesh_vertex(blender_mesh , face , self.quads)
            #we process the face only if this is a triangle
            elif (len(face.verts) == 3) :
                self.add_nds_mesh_vertex(blender_mesh , face , self.triangles)

    """TODO : I think there is a need to rescale the mesh because the range in the NDS is [-8.0, 8.0[ but I need to do some tests before"""
    def rescale_mesh(self,blender_mesh):
        max_x=max_y=max_z=min_x=min_y=min_z=max_l=0
        for v in blender_mesh.verts:
            if v.co[0]>max_x : max_x = v.co[0]
            elif v.co[0]<min_x : min_x = v.co[0]
            if v.co[1]>max_y : max_y = v.co[1]
            elif v.co[1]<min_y : min_y = v.co[1]
            if v.co[2]>max_z : max_z = v.co[2]
            elif v.co[2]<min_z : min_z = v.co[2]
        if (abs(max_x-min_x) > max_l) : max_l = abs(max_x-min_x)
        if (abs(max_y-min_y) > max_l) : max_l = abs(max_y-min_y)
        if (abs(max_z-min_z) > max_l) : max_l = abs(max_z-min_z)

        if (len(self.quads)>0):
            for f in self.quads:
                v=f.vertex
                f.vertex.x = v.x/max_l
                f.vertex.y = v.y/max_l
                f.vertex.z = v.z/max_l
        if (len(self.triangles)>0):
            for f in self.triangles:
                v=f.vertex
                f.vertex.x = v.x/max_l
                f.vertex.y = v.y/max_l
                f.vertex.z = v.z/max_l
        print( "longueur max = %s" % (max_l) )

    def prepare_cmdpack(self):
        #If there is at least 1 quad
        if ( len(self.quads) > 0 ) :
            #Begin Quads list
            self.cmdpack_list.add( _nds_cmdpack_begin('GL_QUADS') )

            for i in range( len(self.quads) ) :

                v = self.quads[i]

                if ( self.options.color_export and v.color != None ) :
                    self.cmdpack_list.add(v.color)

                if (self.options.uv_export and v.uv != None) :
                    self.cmdpack_list.add(v.uv)

                if (self.options.normals_export and v.normal != None):
                    self.cmdpack_list.add(v.normal)

                if (v.vertex != None) :
                    self.cmdpack_list.add(v.vertex)
            #End Quads list
            self.cmdpack_list.add( _nds_cmdpack_end() )

        #If there is at least 1 triangle
        if ( len(self.triangles) > 0 ) :
            #Begin Triangles list
            self.cmdpack_list.add( _nds_cmdpack_begin('GL_TRIANGLES') )

            for i in range( len(self.triangles) ) :

                v = self.triangles[i]

                if ( self.options.color_export and v.color != None ) :
                    self.cmdpack_list.add(v.color)

                if (self.options.uv_export and v.uv != None) :
                    self.cmdpack_list.add(v.uv)

                if (self.options.normals_export and v.normal != None):
                    self.cmdpack_list.add(v.normal)

                if (v.vertex != None) :
                    self.cmdpack_list.add(v.vertex)
            #End Quads list
            self.cmdpack_list.add( _nds_cmdpack_end() )

        #Fill the remaining cmd slots with NOP commands
        self.cmdpack_list.terminate()

    def construct_cmdpack(self):


        if (self.options.format == EXPORT_OPTIONS['FORMAT_TEXT']) :
            s = "u32 %s[] = {\n%d,\n%s" % ( self.options.mesh_name , self.cmdpack_list.get_nb_params() , self.cmdpack_list.get_pack(self.options.format) )
            self.final_cmdpack = ""
            self.final_cmdpack += s[0:-2]
            self.final_cmdpack += "\n};\n"
#            print(self.final_cmdpack)
        elif (self.options.format == EXPORT_OPTIONS['FORMAT_BINARY']) :
            self.final_cmdpack = []
            self.final_cmdpack += struct.pack( '<i' , self.cmdpack_list.get_nb_params())
            self.final_cmdpack += self.cmdpack_list.get_pack(self.options.format)


    def save(self) :
        
        print( 'saving %s in path %s' % (self,self.options.get_final_path_mesh()))
        f = open(self.options.get_final_path_mesh(),"w")
        f.write(self.final_cmdpack)
        f.close();

        if (self.options.texfile_export) : self.save_tex()

    def __str__(self):
        return "NDS Mesh [%s], Faces = %d (Quads=%d, Triangles=%d), Texture=%s" % (self.name,len(self.quads)/4+len(self.triangles)/3,len(self.quads)/4,len(self.triangles)/3,repr((self.options.get_final_path_tex(), self.options.texture_w,self.options.texture_h)) )


class _menu_nds_export (object) :
    __slots__ = 'nb_meshes', 'mesh_options','selected_menu_mesh','popup_elm','button' , 'texID' , 'nds_export'

    def __init__(self,properties, context):
        print ( dir(properties.meshes) )
        if (len(properties.meshes) == 0):
            self.nds_list_meshes(context)

    def nds_list_meshes(self , context) :
        print( "List Meshes in data" )

        if ( len(self.properties.meshes) == 0) :
            meshes = None
            if hasattr(context,'selected_objects'):
                meshes = context.selected_objects


        self.nb_meshes = 0
        self.mesh_options = []
        if meshes:
            for mesh in meshes :
                if (type(mesh.data)==bpy.types.Mesh) :
                    self.mesh_options.append( _mesh_options( mesh.data , dir_path) )
                    self.nb_meshes += 1

        button = []

        if(self.nb_meshes > 0) :
            self.nds_export = _nds_mesh(self.mesh_options[0])


class ExportNDS(bpy.types.Operator) :
    '''Export to Nintendo DS Binary CallList'''
    bl_idname = "export.nds"
    bl_label = "Export Nintendo DS"

    path = bpy.props.StringProperty(name='Path' , description="Path used for exporting Nintendo DS Binary CallList" , maxlen=1024 , default="")
    filename = bpy.props.StringProperty(name='FileName' , description="FileName used for exporting Nintendo DS Binary CallList" , maxlen=1024 , default="")
    directory = bpy.props.StringProperty(name='Directory' , description="Directory used for exporting Nintendo DS Binary CallList" , maxlen=1024 , default="")

    def execute(self , context) :
        print("Path:%s" % self.properties.path)
        print("Filename:%s" % self.properties.filename)
        print("Directory:%s" % self.properties.directory)

        meshes = []

#        print(dir(context.main))

        if ( hasattr(context , 'selected_objects') ):
            for obj in context.selected_objects :
                if ( type(obj) == bpy.types.Mesh ) :
                    meshes.append( _nds_mesh( _mesh_options( obj.data , self.properties.directory ) ) )
        else : #Export all exportable meshes (means we are in background mode)
            for mesh in context.main.meshes :
                print('building export of mesh %s' % mesh.name)
                meshes.append( _nds_mesh( _mesh_options( mesh , self.properties.directory) ) )
        
        for m in meshes:
            m.save()
            

        return ('FINISHED',)

    def invoke(self, context, event) :
        wm = context.manager
        wm.add_fileselect(self)
        return ('RUNNING_MODAL',)

#    def poll(self, context):
#        print("NDS Poll")
#        return True

    
bpy.ops.add(ExportNDS)

# Add to a menu
import dynamic_menu

def menu_func(self, context):
    default_path = bpy.data.filename.replace(".blend", ".bin")
    self.layout.operator(ExportNDS.bl_idname, text=ExportNDS.bl_label).path = default_path

menu_item = dynamic_menu.add(bpy.types.INFO_MT_file_export, menu_func)
    

if __name__ == "__main__" :
    print("I'm running from command-line ;) ...")
#    print( dir(bpy.ops.export.nds.get_rna().bl_rna.functions) )
    print( "Blender File : %s" % bpy.context.main.filename )

   
    import sys
    
    script_args_index = sys.argv.index('--')
    print(sys.argv)
    print("args index = %d" % script_args_index)
    print("args len = %d" % len( sys.argv[script_args_index] ) )
    if ( len( sys.argv[script_args_index] ) > 1 ) :
        script_args = sys.argv[script_args_index+1:]
    else :
        script_args = []
    print(script_args)


    from optparse import OptionParser
    prog_usage = "usage: blender -b blend_file -P %prog -- [options] filename"
    prog_name = "nds"
    parser = OptionParser(usage=prog_usage,prog=prog_name)

    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")

    parser.add_option("-l", "--list",
                        action="store_const" ,const="list" , dest="command",
                        help="List all meshes")

    parser.add_option("-m" , "--mesh",
                        action="store" , type="string" , dest="meshes", default="all",
                        help="Select one or more meshes to export") 
    

    (prog_options, prog_args) = parser.parse_args(script_args)
    print(prog_options , prog_args)

    if (prog_options.command == 'list'):
        print("List all available meshes")
        for m in bpy.data.meshes :
            print(m.name)
    else :
        bpy.ops.export.nds(directory="/tmp/")
    
    
#def my_callback(filename):
##   if filename.find('/', -2) <= 0: filename += '.h' # add '.h' if the user didn't
#    #print Blender.sys.dirname(filename)
#    DSexport(Blender.sys.dirname(filename))
#
#
#fname = Blender.sys.makename(ext = "")
#Blender.Window.FileSelector(my_callback, "Select a directory","")
