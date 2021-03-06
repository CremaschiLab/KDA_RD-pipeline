
# parse_table_datacmds.py
# This file is automatically generated. Do not edit.
_tabversion = '3.8'

_lr_method = 'LALR'

_lr_signature = '86AB0870EAC2F4D0379925D567E7C813'
    
_lr_action_items = {'SET':([0,3,10,15,16,18,51,75,76,78,82,85,87,90,91,110,111,112,113,115,116,121,137,139,154,],[2,2,-4,-3,-20,-19,2,-18,-17,-16,-14,-12,-8,2,2,133,-13,-11,-7,2,-6,-15,-10,-5,-9,]),'LBRACE':([7,17,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,46,47,48,49,50,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,83,89,94,96,98,100,102,114,117,120,122,123,],[20,51,-83,-85,-81,-92,-89,-91,-87,-93,-94,55,-80,-82,-77,-88,-79,-90,-86,-78,-84,20,20,20,20,90,-65,-67,-63,-74,-71,-73,-69,-75,-76,-62,-64,-59,-70,-61,20,-72,-68,-60,-66,55,55,-58,-57,55,-54,-53,20,-56,-55,-52,-51,]),'STRING':([7,9,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,46,47,48,49,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,83,89,94,96,98,100,102,110,114,117,120,122,123,],[21,40,-83,-85,-81,-92,-89,-91,-87,-93,-94,56,-80,-82,-77,-88,-79,-90,-86,-78,-84,21,21,21,21,-65,-67,-63,-74,-71,-73,-69,-75,-76,-62,-64,-59,-70,-61,21,-72,-68,-60,-66,56,56,-58,-57,56,-54,-53,136,21,-56,-55,-52,-51,]),'COMMA':([7,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,46,47,48,49,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,83,89,94,96,98,100,102,114,117,118,119,120,122,123,129,],[19,-83,-85,-81,-92,-89,-91,-87,-93,-94,54,-80,-82,-77,-88,-79,-90,-86,-78,-84,19,19,19,19,93,93,-65,-67,-63,-74,-71,-73,-69,-75,-76,-62,-64,-59,-70,-61,19,-72,-68,-60,-66,93,93,54,54,-58,-57,54,-54,-53,19,-56,93,93,-55,-52,-51,93,]),'ASTERISK':([7,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,46,47,48,49,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,83,89,93,94,96,98,100,102,114,117,120,122,123,],[22,-83,-85,-81,-92,-89,-91,52,-93,-94,57,-80,-82,-77,-88,-79,73,-86,-78,-84,22,22,22,22,-65,-67,-63,-74,-71,-73,52,-75,-76,-62,-64,-59,-70,-61,22,73,-68,-60,-66,57,57,118,-58,-57,57,-54,-53,22,-56,-55,-52,-51,]),'TR':([7,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,46,47,48,49,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,83,89,94,96,98,100,102,114,117,120,122,123,],[23,-83,-85,-81,-92,-89,-91,-87,-93,-94,58,-80,-82,-77,-88,-79,-90,-86,-78,-84,23,23,23,23,-65,-67,-63,-74,-71,-73,-69,-75,-76,-62,-64,-59,-70,-61,23,-72,-68,-60,-66,58,58,-58,-57,58,-54,-53,23,-56,-55,-52,-51,]),'NONWORD':([7,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,46,47,48,49,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,83,89,94,96,98,100,102,114,117,120,122,123,],[29,-83,-85,-81,-92,-89,-91,-87,-93,-94,63,-80,-82,-77,-88,-79,-90,-86,-78,-84,29,29,29,29,-65,-67,-63,-74,-71,-73,-69,-75,-76,-62,-64,-59,-70,-61,29,-72,-68,-60,-66,63,63,-58,-57,63,-54,-53,29,-56,-55,-52,-51,]),'PARAM':([0,3,10,15,16,18,51,75,76,78,82,85,87,90,91,110,111,112,113,115,116,121,137,139,154,],[7,7,-4,-3,-20,-19,7,-18,-17,-16,-14,-12,-8,7,7,132,-13,-11,-7,7,-6,-15,-10,-5,-9,]),'INCLUDE':([0,3,10,15,16,18,51,75,76,78,82,85,87,90,91,111,112,113,115,116,121,137,139,154,],[8,8,-4,-3,-20,-19,8,-18,-17,-16,-14,-12,-8,8,8,-13,-11,-7,8,-6,-15,-10,-5,-9,]),'LBRACKET':([7,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,46,47,48,49,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,80,83,89,94,96,98,100,102,104,114,117,120,122,123,131,143,],[25,-83,-85,-81,-92,-89,-91,-87,-93,-94,60,-80,-82,-77,-88,-79,-90,-86,-78,-84,25,25,25,25,-65,-67,-63,-74,-71,-73,-69,-75,-76,-62,-64,-59,-70,-61,25,-72,-68,-60,-66,107,60,60,-58,-57,60,-54,-53,107,25,-56,-55,-52,-51,107,107,]),'FILENAME':([9,77,],[43,103,]),'EQ':([81,109,126,128,],[110,131,143,144,]),'DATA':([0,3,10,15,16,18,51,75,76,78,82,85,87,90,91,111,112,113,115,116,121,137,139,154,],[6,6,-4,-3,-20,-19,6,-18,-17,-16,-14,-12,-8,6,6,-13,-11,-7,6,-6,-15,-10,-5,-9,]),'RPAREN':([7,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,46,47,48,49,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,83,89,94,96,98,99,100,101,102,114,117,118,119,120,122,123,140,141,],[24,-83,-85,-81,-92,-89,-91,-87,-93,-94,59,-80,-82,-77,-88,-79,-90,-86,-78,-84,24,24,24,24,-65,-67,-63,-74,-71,-73,-69,-75,-76,-62,-64,-59,-70,-61,24,-72,-68,-60,-66,100,102,59,59,-58,-57,59,122,-54,123,-53,24,-56,-50,-49,-55,-52,-51,-48,-47,]),'SEMICOLON':([4,6,19,20,21,22,23,24,25,26,27,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,54,55,56,57,58,59,60,61,62,63,64,65,66,67,69,70,71,72,79,83,84,86,88,94,96,97,98,100,102,103,105,106,109,114,117,120,122,123,124,126,127,128,130,132,133,134,135,136,138,142,148,149,150,151,152,153,157,158,],[16,18,-83,-85,-81,-92,-89,-91,-87,-93,-94,-80,-82,-77,-88,-79,-90,-86,-78,-84,75,76,-96,-97,-95,-98,78,-24,82,85,87,-65,-67,-63,-74,-71,-73,-69,-75,-76,-62,-64,-59,-70,-61,-72,-68,-60,-66,-23,-21,111,112,113,-58,-57,121,-22,-54,-53,-99,-42,-30,-43,137,-56,-55,-52,-51,-29,-43,-41,-43,-28,-38,-40,-34,-36,-32,154,-27,-44,-37,-39,-33,-35,-31,-26,-25,]),'$end':([0,1,3,10,15,16,18,75,76,78,82,85,87,111,112,113,116,121,137,139,154,],[-2,0,-1,-4,-3,-20,-19,-18,-17,-16,-14,-12,-8,-13,-11,-7,-6,-15,-10,-5,-9,]),'QUOTEDSTRING':([7,8,9,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,46,47,48,49,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,83,89,94,96,98,100,102,110,114,117,120,122,123,],[30,38,41,-83,-85,-81,-92,-89,-91,-87,-93,-94,64,-80,-82,-77,-88,-79,-90,-86,-78,-84,30,30,30,30,-65,-67,-63,-74,-71,-73,-69,-75,-76,-62,-64,-59,-70,-61,30,-72,-68,-60,-66,64,64,-58,-57,64,-54,-53,134,30,-56,-55,-52,-51,]),'NAMESPACE':([0,3,10,15,16,18,51,75,76,78,82,85,87,90,91,111,112,113,115,116,121,137,139,154,],[5,14,-4,-3,-20,-19,5,-18,-17,-16,-14,-12,-8,5,14,-13,-11,-7,14,-6,-15,-10,-5,-9,]),'RBRACKET':([7,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,46,47,48,49,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,83,89,92,94,95,96,98,100,102,114,117,118,119,120,122,123,129,140,141,145,],[32,-83,-85,-81,-92,-89,-91,-87,-93,-94,66,-80,-82,-77,-88,-79,-90,-86,-78,-84,32,32,32,32,94,96,-65,-67,-63,-74,-71,-73,-69,-75,-76,-62,-64,-59,-70,-61,32,-72,-68,-60,-66,66,66,117,-58,120,-57,66,-54,-53,32,-56,-50,-49,-55,-52,-51,146,-48,-47,156,]),'WORDWITHSQUOTEDINDEX':([2,7,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,46,47,48,49,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,83,89,94,96,98,100,102,114,117,120,122,123,],[11,33,-83,-85,-81,-92,-89,-91,-87,-93,-94,67,-80,-82,-77,-88,-79,-90,-86,-78,-84,33,33,33,33,-65,-67,-63,-74,-71,-73,-69,-75,-76,-62,-64,-59,-70,-61,33,-72,-68,-60,-66,67,67,-58,-57,67,-54,-53,33,-56,-55,-52,-51,]),'WORDWITHINDEX':([2,7,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,46,47,48,49,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,83,89,94,96,98,100,102,114,117,120,122,123,],[12,36,-83,-85,-81,-92,-89,-91,-87,-93,-94,71,-80,-82,-77,-88,-79,-90,-86,-78,-84,36,36,36,36,-65,-67,-63,-74,-71,-73,-69,-75,-76,-62,-64,-59,-70,-61,36,-72,-68,-60,-66,71,71,-58,-57,71,-54,-53,36,-56,-55,-52,-51,]),'LPAREN':([7,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,46,47,48,49,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,83,89,94,96,98,100,102,114,117,120,122,123,],[34,-83,-85,-81,-92,-89,-91,-87,-93,-94,69,-80,-82,-77,-88,-79,-90,-86,-78,-84,34,34,34,34,-65,-67,-63,-74,-71,-73,-69,-75,-76,-62,-64,-59,-70,-61,34,-72,-68,-60,-66,69,69,-58,-57,69,-54,-53,34,-56,-55,-52,-51,]),'COLONEQ':([11,12,13,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,54,55,56,57,58,59,60,61,62,63,64,65,66,67,69,70,71,72,89,94,96,100,102,117,120,122,123,],[46,47,48,-83,-85,-81,-92,-89,-91,-87,-93,-94,68,-80,-82,-77,-88,-79,-90,-86,-78,-84,-65,-67,-63,-74,-71,-73,-69,-75,-76,-62,-64,-59,-70,-61,-72,-68,-60,-66,114,-58,-57,-54,-53,-56,-55,-52,-51,]),'RBRACE':([7,10,15,16,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,46,47,48,49,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,75,76,78,82,83,85,87,89,91,94,96,98,100,102,111,112,113,114,115,116,117,120,121,122,123,137,139,154,],[35,-4,-3,-20,-19,-83,-85,-81,-92,-89,-91,-87,-93,-94,70,-80,-82,-77,-88,-79,-90,-86,-78,-84,35,35,35,35,-65,-67,-63,-74,-71,-73,-69,-75,-76,-62,-64,-59,-70,-61,35,-72,-68,-60,-66,-18,-17,-16,-14,70,-12,-8,70,116,-58,-57,70,-54,-53,-13,-11,-7,35,139,-6,-56,-55,-15,-52,-51,-10,-5,-9,]),'IMPORT':([0,3,10,15,16,18,51,75,76,78,82,85,87,90,91,111,112,113,115,116,121,137,139,154,],[9,9,-4,-3,-20,-19,9,-18,-17,-16,-14,-12,-8,9,9,-13,-11,-7,9,-6,-15,-10,-5,-9,]),'END':([0,3,10,15,16,18,51,75,76,78,82,85,87,90,91,111,112,113,115,116,121,137,139,154,],[4,4,-4,-3,-20,-19,4,-18,-17,-16,-14,-12,-8,4,4,-13,-11,-7,4,-6,-15,-10,-5,-9,]),'COLON':([7,13,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,40,41,42,43,45,46,47,48,49,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,79,83,89,94,96,98,100,102,103,114,117,120,122,123,132,133,134,135,136,149,150,151,152,153,],[37,49,-83,-85,-81,-92,-89,-91,-87,-93,-94,72,-80,-82,-77,-88,-79,-90,-86,-78,-84,-96,-97,77,-98,80,37,37,37,37,-65,-67,-63,-74,-71,-73,-69,-75,-76,-62,-64,-59,-70,-61,37,-72,-68,-60,-66,104,72,72,-58,-57,72,-54,-53,-99,37,-56,-55,-52,-51,-38,-40,-34,-36,-32,-37,-39,-33,-35,-31,]),'WORD':([2,5,7,8,9,14,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,40,41,42,43,45,46,47,48,49,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,80,83,89,93,94,96,98,100,102,103,104,105,107,108,109,110,114,117,120,122,123,125,126,128,131,132,133,134,135,136,143,144,146,147,148,155,156,],[13,17,31,39,42,50,-83,-85,-81,-92,-89,-91,53,-93,-94,65,-80,-82,-77,-88,-79,74,-86,-78,-84,-96,-97,-95,-98,81,31,31,31,31,-65,-67,-63,-74,-71,-73,53,-75,-76,-62,-64,-59,-70,-61,31,74,-68,-60,-66,109,65,65,119,-58,-57,65,-54,-53,-99,126,128,129,128,-43,135,31,-56,-55,-52,-51,128,-43,-43,148,81,81,81,81,81,148,148,-46,128,-44,128,-45,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'expr':([0,],[1,]),'index_list':([52,53,73,74,118,119,129,],[92,95,99,101,140,141,145,]),'statement':([0,3,51,90,91,115,],[10,15,10,10,15,15,]),'items':([7,46,47,48,49,68,114,],[28,83,83,83,89,98,83,]),'set_template':([7,28,46,47,48,49,68,83,89,98,114,],[26,61,26,26,26,26,26,61,61,61,26,]),'import_options':([45,132,133,134,135,136,],[79,149,150,151,152,153,]),'paramdecl':([68,],[97,]),'indices':([80,104,131,143,],[108,125,147,155,]),'param_template':([7,28,46,47,48,49,68,83,89,98,114,],[27,62,27,27,27,27,27,62,62,62,27,]),'statements':([0,51,90,],[3,91,115,]),'variable':([80,104,105,108,125,147,155,],[105,105,105,105,105,105,105,]),'setdecl':([46,47,48,114,],[84,86,88,138,]),'variable_options':([80,104,105,108,125,147,155,],[106,124,127,130,142,157,158,]),'importdecl':([9,],[44,]),'filename':([9,],[45,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> expr","S'",1,None,None,None),
  ('expr -> statements','expr',1,'p_expr','parse_data_cmds.py',151),
  ('expr -> <empty>','expr',0,'p_expr','parse_data_cmds.py',152),
  ('statements -> statements statement','statements',2,'p_statements','parse_data_cmds.py',166),
  ('statements -> statement','statements',1,'p_statements','parse_data_cmds.py',167),
  ('statements -> statements NAMESPACE WORD LBRACE statements RBRACE','statements',6,'p_statements','parse_data_cmds.py',168),
  ('statements -> NAMESPACE WORD LBRACE statements RBRACE','statements',5,'p_statements','parse_data_cmds.py',169),
  ('statement -> SET WORD COLONEQ setdecl SEMICOLON','statement',5,'p_statement','parse_data_cmds.py',191),
  ('statement -> SET WORD COLONEQ SEMICOLON','statement',4,'p_statement','parse_data_cmds.py',192),
  ('statement -> SET WORD COLON items COLONEQ setdecl SEMICOLON','statement',7,'p_statement','parse_data_cmds.py',193),
  ('statement -> SET WORD COLON items COLONEQ SEMICOLON','statement',6,'p_statement','parse_data_cmds.py',194),
  ('statement -> SET WORDWITHINDEX COLONEQ setdecl SEMICOLON','statement',5,'p_statement','parse_data_cmds.py',195),
  ('statement -> SET WORDWITHINDEX COLONEQ SEMICOLON','statement',4,'p_statement','parse_data_cmds.py',196),
  ('statement -> SET WORDWITHSQUOTEDINDEX COLONEQ setdecl SEMICOLON','statement',5,'p_statement','parse_data_cmds.py',197),
  ('statement -> SET WORDWITHSQUOTEDINDEX COLONEQ SEMICOLON','statement',4,'p_statement','parse_data_cmds.py',198),
  ('statement -> PARAM items COLONEQ paramdecl SEMICOLON','statement',5,'p_statement','parse_data_cmds.py',199),
  ('statement -> IMPORT importdecl SEMICOLON','statement',3,'p_statement','parse_data_cmds.py',200),
  ('statement -> INCLUDE WORD SEMICOLON','statement',3,'p_statement','parse_data_cmds.py',201),
  ('statement -> INCLUDE QUOTEDSTRING SEMICOLON','statement',3,'p_statement','parse_data_cmds.py',202),
  ('statement -> DATA SEMICOLON','statement',2,'p_statement','parse_data_cmds.py',203),
  ('statement -> END SEMICOLON','statement',2,'p_statement','parse_data_cmds.py',204),
  ('setdecl -> items','setdecl',1,'p_setdecl','parse_data_cmds.py',219),
  ('paramdecl -> items','paramdecl',1,'p_paramdecl','parse_data_cmds.py',223),
  ('importdecl -> filename import_options','importdecl',2,'p_importdecl','parse_data_cmds.py',227),
  ('importdecl -> filename','importdecl',1,'p_importdecl','parse_data_cmds.py',228),
  ('importdecl -> filename import_options COLON WORD EQ indices variable_options','importdecl',7,'p_importdecl','parse_data_cmds.py',229),
  ('importdecl -> filename COLON WORD EQ indices variable_options','importdecl',6,'p_importdecl','parse_data_cmds.py',230),
  ('importdecl -> filename import_options COLON indices variable_options','importdecl',5,'p_importdecl','parse_data_cmds.py',231),
  ('importdecl -> filename COLON indices variable_options','importdecl',4,'p_importdecl','parse_data_cmds.py',232),
  ('importdecl -> filename import_options COLON variable_options','importdecl',4,'p_importdecl','parse_data_cmds.py',233),
  ('importdecl -> filename COLON variable_options','importdecl',3,'p_importdecl','parse_data_cmds.py',234),
  ('import_options -> WORD EQ STRING import_options','import_options',4,'p_import_options','parse_data_cmds.py',262),
  ('import_options -> WORD EQ STRING','import_options',3,'p_import_options','parse_data_cmds.py',263),
  ('import_options -> WORD EQ QUOTEDSTRING import_options','import_options',4,'p_import_options','parse_data_cmds.py',264),
  ('import_options -> WORD EQ QUOTEDSTRING','import_options',3,'p_import_options','parse_data_cmds.py',265),
  ('import_options -> WORD EQ WORD import_options','import_options',4,'p_import_options','parse_data_cmds.py',266),
  ('import_options -> WORD EQ WORD','import_options',3,'p_import_options','parse_data_cmds.py',267),
  ('import_options -> WORD EQ PARAM import_options','import_options',4,'p_import_options','parse_data_cmds.py',268),
  ('import_options -> WORD EQ PARAM','import_options',3,'p_import_options','parse_data_cmds.py',269),
  ('import_options -> WORD EQ SET import_options','import_options',4,'p_import_options','parse_data_cmds.py',270),
  ('import_options -> WORD EQ SET','import_options',3,'p_import_options','parse_data_cmds.py',271),
  ('variable_options -> variable variable_options','variable_options',2,'p_variable_options','parse_data_cmds.py',281),
  ('variable_options -> variable','variable_options',1,'p_variable_options','parse_data_cmds.py',282),
  ('variable -> WORD','variable',1,'p_variable','parse_data_cmds.py',291),
  ('variable -> WORD EQ WORD','variable',3,'p_variable','parse_data_cmds.py',292),
  ('indices -> LBRACKET WORD index_list RBRACKET','indices',4,'p_indices','parse_data_cmds.py',300),
  ('indices -> LBRACKET WORD RBRACKET','indices',3,'p_indices','parse_data_cmds.py',301),
  ('index_list -> COMMA WORD index_list','index_list',3,'p_index_list','parse_data_cmds.py',310),
  ('index_list -> COMMA ASTERISK index_list','index_list',3,'p_index_list','parse_data_cmds.py',311),
  ('index_list -> COMMA WORD','index_list',2,'p_index_list','parse_data_cmds.py',312),
  ('index_list -> COMMA ASTERISK','index_list',2,'p_index_list','parse_data_cmds.py',313),
  ('set_template -> LPAREN WORD index_list RPAREN','set_template',4,'p_set_template','parse_data_cmds.py',322),
  ('set_template -> LPAREN ASTERISK index_list RPAREN','set_template',4,'p_set_template','parse_data_cmds.py',323),
  ('set_template -> LPAREN WORD RPAREN','set_template',3,'p_set_template','parse_data_cmds.py',324),
  ('set_template -> LPAREN ASTERISK RPAREN','set_template',3,'p_set_template','parse_data_cmds.py',325),
  ('param_template -> LBRACKET WORD index_list RBRACKET','param_template',4,'p_param_template','parse_data_cmds.py',333),
  ('param_template -> LBRACKET ASTERISK index_list RBRACKET','param_template',4,'p_param_template','parse_data_cmds.py',334),
  ('param_template -> LBRACKET WORD RBRACKET','param_template',3,'p_param_template','parse_data_cmds.py',335),
  ('param_template -> LBRACKET ASTERISK RBRACKET','param_template',3,'p_param_template','parse_data_cmds.py',336),
  ('items -> items WORD','items',2,'p_items','parse_data_cmds.py',347),
  ('items -> items WORDWITHINDEX','items',2,'p_items','parse_data_cmds.py',348),
  ('items -> items WORDWITHSQUOTEDINDEX','items',2,'p_items','parse_data_cmds.py',349),
  ('items -> items NONWORD','items',2,'p_items','parse_data_cmds.py',350),
  ('items -> items STRING','items',2,'p_items','parse_data_cmds.py',351),
  ('items -> items QUOTEDSTRING','items',2,'p_items','parse_data_cmds.py',352),
  ('items -> items COMMA','items',2,'p_items','parse_data_cmds.py',353),
  ('items -> items COLON','items',2,'p_items','parse_data_cmds.py',354),
  ('items -> items LBRACE','items',2,'p_items','parse_data_cmds.py',355),
  ('items -> items RBRACE','items',2,'p_items','parse_data_cmds.py',356),
  ('items -> items LBRACKET','items',2,'p_items','parse_data_cmds.py',357),
  ('items -> items RBRACKET','items',2,'p_items','parse_data_cmds.py',358),
  ('items -> items TR','items',2,'p_items','parse_data_cmds.py',359),
  ('items -> items LPAREN','items',2,'p_items','parse_data_cmds.py',360),
  ('items -> items RPAREN','items',2,'p_items','parse_data_cmds.py',361),
  ('items -> items ASTERISK','items',2,'p_items','parse_data_cmds.py',362),
  ('items -> items set_template','items',2,'p_items','parse_data_cmds.py',363),
  ('items -> items param_template','items',2,'p_items','parse_data_cmds.py',364),
  ('items -> WORD','items',1,'p_items','parse_data_cmds.py',365),
  ('items -> WORDWITHINDEX','items',1,'p_items','parse_data_cmds.py',366),
  ('items -> WORDWITHSQUOTEDINDEX','items',1,'p_items','parse_data_cmds.py',367),
  ('items -> NONWORD','items',1,'p_items','parse_data_cmds.py',368),
  ('items -> STRING','items',1,'p_items','parse_data_cmds.py',369),
  ('items -> QUOTEDSTRING','items',1,'p_items','parse_data_cmds.py',370),
  ('items -> COMMA','items',1,'p_items','parse_data_cmds.py',371),
  ('items -> COLON','items',1,'p_items','parse_data_cmds.py',372),
  ('items -> LBRACE','items',1,'p_items','parse_data_cmds.py',373),
  ('items -> RBRACE','items',1,'p_items','parse_data_cmds.py',374),
  ('items -> LBRACKET','items',1,'p_items','parse_data_cmds.py',375),
  ('items -> RBRACKET','items',1,'p_items','parse_data_cmds.py',376),
  ('items -> TR','items',1,'p_items','parse_data_cmds.py',377),
  ('items -> LPAREN','items',1,'p_items','parse_data_cmds.py',378),
  ('items -> RPAREN','items',1,'p_items','parse_data_cmds.py',379),
  ('items -> ASTERISK','items',1,'p_items','parse_data_cmds.py',380),
  ('items -> set_template','items',1,'p_items','parse_data_cmds.py',381),
  ('items -> param_template','items',1,'p_items','parse_data_cmds.py',382),
  ('filename -> WORD','filename',1,'p_filename','parse_data_cmds.py',404),
  ('filename -> STRING','filename',1,'p_filename','parse_data_cmds.py',405),
  ('filename -> QUOTEDSTRING','filename',1,'p_filename','parse_data_cmds.py',406),
  ('filename -> FILENAME','filename',1,'p_filename','parse_data_cmds.py',407),
  ('filename -> WORD COLON FILENAME','filename',3,'p_filename','parse_data_cmds.py',408),
]
