from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from bs4 import BeautifulSoup
import cv2
import pathlib
import blue_detect
from blue_detect import blurDetect


class Xml_Generate: 
    def clipItem(self, track1, dir, files, dlg):
        global total_file
        global end_frame
        global transition_length
        global fps
        global video_files 
        i = 0
        k = 0
        n = 0
        flag = 0
        fixed_duration = 0
        str_frame = 0
        end_frame = 0
        fps = int(dlg.lineEdit_fps.text())
        total_file = len(files)
        video_files = [[1 for x in range(6)] for y in range(total_file)]
        auto_duration = [[0 for x in range(total_file)] for y in range(2)] 
        transition_length = int(dlg.lineEdit_transition_length.text())
        if (dlg.lineEdit_duration_clip.text() != ''):
            duration_perclip =fps * (int(dlg.lineEdit_duration_clip.text()))
        if(dlg.lineEdit_maxduration.text()!=''):
            print("Computing duration...")
            d_max = fps * (int(dlg.lineEdit_maxduration.text()) * 60 )
            d_perclip = int(d_max / (total_file))

            for file in files:
                path = dir + '/' +file
                d = cv2.VideoCapture(path)
                d_frame = int(d.get(cv2.CAP_PROP_FRAME_COUNT))
                auto_duration[0][n] = d_frame
                if(d_frame<=d_perclip):
                    auto_duration[1][n] = 1
                    fixed_duration += d_frame
                    flag += 1
                n+=1
            while(flag!=total_file):
                d_max -= fixed_duration
                d_perclip = int(d_max / (total_file - flag))
                for i in range(total_file): 
                    if(auto_duration[1][i]!=1 and auto_duration[0][i]<=d_perclip):
                        auto_duration[1][i] = 1
                        fixed_duration += auto_duration[0][i]
                        flag += 1
                    elif(auto_duration[1][i]!=1 and auto_duration[0][i]>=d_perclip):
                        auto_duration[1][i] = 1
                        fixed_duration += auto_duration[0][i]
                        auto_duration[0][i] = d_perclip
                        flag +=1                     




        print("Processing Files...")
        i = 0
        for file in files:
            i += 1
            j = 0
            path = dir + '/' + file
            v = cv2.VideoCapture(path)
            #fps = v.get(cv2.CAP_PROP_FPS)
            frame_count = int(v.get(cv2.CAP_PROP_FRAME_COUNT))
            f_height= int(v.get(cv2.CAP_PROP_FRAME_HEIGHT))
            f_width = int(v.get(cv2.CAP_PROP_FRAME_WIDTH))
            video_files[k][j] = file # matrix to store data for audio track
            j+=1
            video_files[k][j] = frame_count
            if (dlg.lineEdit_duration_clip.text() != '' and dlg.lineEdit_maxduration.text()!=''):
                duration_perclip = auto_duration[0][i-1]
            elif(dlg.lineEdit_maxduration.text()==''):
                duration_perclip =fps * (int(dlg.lineEdit_duration_clip.text()))
            else:
                duration_perclip = 0

            print('======================================')
            print(path)
            print('resolution=',f_width,'x',f_height)
            print('fps =',fps)

            if (dlg.lineEdit_speed.text() != ''):
                speed = float(dlg.lineEdit_speed.text())
                speed = speed / 100 + ((fps + 10) / 100)
            else:
                speed = 1
            clipitem = SubElement(track1, 'clipitem', id='clipitem-' + str(i))
            masterclipid = SubElement(clipitem, 'masterclipid')
            masterclipid.text = 'masterclip-' + str(i)
            name = SubElement(clipitem, 'name')
            name.text = file
            enabled = SubElement(clipitem, 'enabled')
            enabled.text = 'TRUE'
            c_duration = SubElement(clipitem, 'duration')
            c_duration.text = str(frame_count)
            c_rate = SubElement(clipitem, 'rate')
            c_timebase = SubElement(c_rate, 'timebase')
            c_timebase.text = str(fps)
            c_ntsc = SubElement(c_rate, 'ntsc')
            c_ntsc.text = 'FALSE'
            start = SubElement(clipitem, 'start')
            if dlg.checkBox_addtransition.isChecked():
                if (i == 1):
                    start.text = '0'
                else:
                    start.text = '-1'
                    str_frame = end_frame
            else:
                if (i == 1):
                    start.text = '0'

                else:
                    start.text = str(end_frame)
                    str_frame = end_frame

            j+=1
            video_files[k][j] = str_frame # matrix to store data for audio track

            end = SubElement(clipitem, 'end')

            if (dlg.checkBox_addtransition.isChecked() and i != total_file):
                end.text = '-1'
                end_fram = end_frame + (duration_perclip / speed)
                if(end_fram-str_frame>frame_count):
                    end_frame = end_frame + (frame_count /speed) - transition_length
                else:
                    end_frame = end_frame + (duration_perclip /speed) - transition_length
            else:
                if (duration_perclip != 0):
                    end_fram = end_frame + (duration_perclip / speed)
                    if(end_fram-str_frame>frame_count):
                        end_frame = end_frame + (frame_count /speed)
                        end.text = str(end_frame)
                    else:
                        end_frame = end_frame+(duration_perclip /speed)
                        end.text = str(end_frame)
                else:
                    end_frame = end_frame + (frame_count / speed)
                    end.text = str(end_frame)
            j+=1
            video_files[k][j] = end_frame # matrix to store data for audio track

            inn = SubElement(clipitem, 'in')
            if dlg.checkBox_Blur.isChecked():
                if(duration_perclip!=0):
                    s_frame = int((frame_count / 2) - (duration_perclip / 2))
                else:
                    s_frame = 0
                blr  = blurDetect(path,s_frame,duration_perclip)
                while(blr!=1):
                    s_frame = s_frame+duration_perclip
                    blr = blurDetect(path,s_frame, duration_perclip)
                print('start frame : ',s_frame)
                inn.text = str(s_frame)
                j+=1
                video_files[k][j] = s_frame # matrix to store data for audio track

            else:
                if(duration_perclip!=0 and frame_count>duration_perclip):
                    inn.text = str(int((frame_count/2)-(duration_perclip*speed)/2))
                    #inn.text = str(int((frame_count/2)-(duration_perclip/2)/speed))
                    j+=1
                    video_files[k][j] = int((frame_count/2)-(duration_perclip*speed)/2) # matrix to store data for audio track

                else:
                    inn.text = '0'  # start video from in frame
                    j+=1
                    video_files[k][j] = 0 # matrix to store data for audio track

            out = SubElement(clipitem, 'out')
            out.text = str(frame_count)
            j+=1
            video_files[k][j]=frame_count
            alphatype = SubElement(clipitem, 'alphatype')
            alphatype.text = 'none'
            c_pixelaspectratio = SubElement(clipitem, 'pixelaspectratio')
            c_pixelaspectratio.text = 'sqare'
            anamorphic = SubElement(clipitem, 'anamorphic')
            anamorphic.text = 'FALSE'
            c_file = SubElement(clipitem, 'file', id='file-' + str(i))
            f_name = SubElement(c_file, 'name')
            f_name.text = file
            pathurl = SubElement(c_file, 'pathurl')
            #path = pathlib.Path(path).as_uri()
            #path = path.replace('file://', 'file://localhost')
            #firstchar = path[:6]
            #path = path[6:].replace(':', '%3a')
            pathurl.text = str(file)
            f_rate = SubElement(c_file, 'rate')
            f_timebase = SubElement(f_rate, 'timebase')
            f_timebase.text = str(fps)
            f_ntsc = SubElement(f_rate, 'ntsc')
            f_ntsc.text = 'FALSE'
            timecode = SubElement(c_file, 'timecode')
            t_rate = SubElement(timecode, 'rate')
            t_timebase = SubElement(t_rate, 'timebase')
            t_timebase.text = str(fps)
            t_ntsc = SubElement(t_rate, 'ntsc')
            t_ntsc.text = 'FALSE'
            displayformat = SubElement(timecode, 'displayformat')
            displayformat.text = 'NDF'
            media = SubElement(c_file, 'media')
            video = SubElement(media, 'video')
            v_samplecharacteristics = SubElement(video, 'samplecharacteristics')
            s_rate = SubElement(v_samplecharacteristics, 'rate')
            s_timebase = SubElement(s_rate, 'timebase')
            s_timebase.text = str(fps)
            s_ntsc = SubElement(s_rate, 'ntsc')
            s_ntsc.text = 'FALSE'
            s_width = SubElement(v_samplecharacteristics, 'width')
            s_width.text = str(f_width)
            s_height = SubElement(v_samplecharacteristics, 'height')
            s_height.text = str(f_height)
            s_anamorphic = SubElement(v_samplecharacteristics, 'anamorphic')
            s_anamorphic.text = 'FALSE'
            s_pixelaspectratio = SubElement(v_samplecharacteristics, 'pixelaspectratio')
            s_pixelaspectratio.text = 'sqare'
            s_fielddominance = SubElement(v_samplecharacteristics, 'fielddominance')
            s_fielddominance.text = 'none'
            m_audio = SubElement(media, 'audio')
            a_samplecharacteristics = SubElement(m_audio,'samplecharacteristics')
            a_depth = SubElement(a_samplecharacteristics,'depth')
            a_depth.text = '16'
            a_samplerate = SubElement(a_samplecharacteristics,'samplerate')
            a_samplerate.text = '48000'
            a_channelcount = SubElement(m_audio,'channelcount')
            a_channelcount.text = '2'

            v_link = SubElement(clipitem,'link')
            v_linkclipref = SubElement(v_link,'linkclipref')
            v_linkclipref.text = 'clipitem-'+str(i)
            v_mediatype = SubElement(v_link,'mediatype')
            v_mediatype.text = 'video'
            v_trackindex = SubElement(v_link,'trackindex')
            v_trackindex.text = '1'
            v_clipindex = SubElement(v_link,'clipindex')
            if(i==1):
                v_clipindex.text = str(i)
            else:
                v_clipindex.text = str(i+i-1)


            link = SubElement(clipitem,'link')
            linkclipref = SubElement(link,'linkclipref')
            linkclipref.text = 'clipitem-'+str(total_file+i)
            mediatype = SubElement(link,'mediatype')
            mediatype.text = 'audio'
            trackindex = SubElement(link,'trackindex')
            trackindex.text = '1'
            clipindex = SubElement(link,'clipindex')
            clipindex.text = str(i)
  
            if (dlg.checkBox_addtransition.isChecked() and i != total_file):
                transition = SubElement(track1, 'transitionitem')
                t_start = SubElement(transition, 'start')
                t_start.text = str(end_frame - transition_length)
                t_end = SubElement(transition, 'end')
                t_end.text = str(end_frame)
                alignment = SubElement(transition, 'alignment')
                alignment.text = 'center'
                t_rate = SubElement(transition, 'rate')
                tr_timebase = SubElement(t_rate, 'timebase')
                tr_timebase.text = str(fps)
                tr_ntsc = SubElement(t_rate, 'ntsc')
                tr_ntsc.text = 'FALSE'
                effect = SubElement(transition, 'effect')
                e_name = SubElement(effect, 'name')
                e_name.text = 'Cross Dissolve'
                e_effectid = SubElement(effect, 'effectid')
                e_effectid.text = 'Cross Dissolve'
                e_effectcategory = SubElement(effect, 'effectcategory')
                e_effectcategory.text = 'Dissolve'
                e_effecttype = SubElement(effect, 'effecttype')
                e_effecttype.text = 'transition'
                e_mediatype = SubElement(effect, 'mediatype')
                e_mediatype.text = 'video'
                e_wipecode = SubElement(effect, 'wipecode')
                e_wipecode.text = '0'
                e_wipeaccuracy = SubElement(effect, 'wipeaccuracy')
                e_wipeaccuracy.text = '100'
                e_startratio = SubElement(effect, 'startratio')
                e_startratio.text = '0'
                e_endratio = SubElement(effect, 'endratio')
                e_endratio.text = '1'
                e_reverse = SubElement(effect, 'reverse')
                e_reverse.text = 'FALSE'
            if (dlg.lineEdit_speed.text() != ''):
                filter = SubElement(clipitem, 'filter')
                f_effect = SubElement(filter, 'effect')
                f_name = SubElement(f_effect, 'name')
                f_name.text = 'Time Remap'
                f_effectid = SubElement(f_effect, 'effectid')
                f_effectid.text = 'timeremap'
                f_effectcategory = SubElement(f_effect, 'effectcategory')
                f_effectcategory.text = 'motion'
                f_effecttype = SubElement(f_effect, 'effecttype')
                f_effecttype.text = 'motion'
                f_mediatype = SubElement(f_effect, 'mediatype')
                f_mediatype.text = 'video'
                f_parameter = SubElement(f_effect, 'parameter', authoringApp="PremierePro")
                f_parameterid = SubElement(f_parameter, 'parameterid')
                f_parameterid.text = 'speed'
                p_name = SubElement(f_parameter, 'name')
                p_name.text = 'speed'
                f_valuemin = SubElement(f_parameter, 'valuemin')
                f_valuemin.text = '-100000'
                f_valuemax = SubElement(f_parameter, 'valuemax')
                f_valuemax.text = '100000'
                f_value = SubElement(f_parameter, 'value')
                f_value.text = str(dlg.lineEdit_speed.text())
            dlg.progressBar.setValue((i/total_file)*100)
            k += 1
        
    def audioTrack(self,media,dlg):
        audio = SubElement(media, 'audio')
        numOutputChannels = SubElement(audio, 'numOutputChannels')
        numOutputChannels.text = '2'
        a_format = SubElement(audio, 'format')
        f_samplecharacteristics = SubElement(a_format, 'samplecharacteristics')
        f_depth = SubElement(f_samplecharacteristics, 'depth')
        f_depth.text = '16'
        f_samplerate = SubElement(f_samplecharacteristics, 'samplerate')
        f_samplerate.text = '48000'
        a_output = SubElement(audio, 'output')
        a_group = SubElement(a_output, 'group')
        a_index = SubElement(a_group, 'index')
        a_index.text = '1'
        a_numchabbels = SubElement(a_group, 'numchannels')
        a_numchabbels.text = '1'
        a_downmix = SubElement(a_group, 'downmix')
        a_downmix.text = '0'
        a_channel = SubElement(a_group , 'channel')
        c_index = SubElement(a_channel , 'index')
        c_index.text = '1'
        a_group1 = SubElement(a_output, 'group')
        a_index1 = SubElement(a_group1, 'index')
        a_index1.text = '2'
        a_numchabbels1 = SubElement(a_group1, 'numchannels')
        a_numchabbels1.text = '1'
        a_downmix1 = SubElement(a_group1, 'downmix')
        a_downmix1.text = '0'
        a_channel1 = SubElement(a_group1 , 'channel')
        c_index1 = SubElement(a_channel1 , 'index')
        c_index1.text = '2'

        track4 = SubElement(audio, 'track')
        track4.set('TL.SQTrackAudioKeyframeStyle','0') 
        track4.set('TL.SQTrackShy', '0')
        track4.set('TL.SQTrackExpandedHeight', '25')
        track4.set('TL.SQTrackExpanded', '0')
        track4.set('MZ.TrackTargeted', '1')
        track4.set('PannerCurrentValue','0.5')
        track4.set('PannerIsInverted','true')
        track4.set('PannerStartKeyframe','-91445760000000000,0.5,0,0,0,0,0,0')
        track4.set('PannerName','Balance')
        track4.set('currentExplodedTrackIndex','0')
        track4.set('totalExplodedTrackCount','2')
        track4.set('premiereTrackType','Stereo')
        k = 0
        i = total_file
        while(k!=total_file):
            i+=1
            a_clipitem = SubElement(track4,'clipitem', id='clipitem-'+str(i) ,premiereChannelType='stereo')
            a_masterclipid = SubElement(a_clipitem, 'masterclipid')
            a_masterclipid.text = 'masterclip-' + str(k+1)
            a_name = SubElement(a_clipitem, 'name')
            a_name.text = str(video_files[k][0])
            a_enabled = SubElement(a_clipitem, 'enabled')
            a_enabled.text = 'TRUE'
            a_duration = SubElement(a_clipitem, 'duration')
            a_duration.text = str(video_files[k][1])
            a_rate = SubElement(a_clipitem, 'rate')
            a_timebase = SubElement(a_rate, 'timebase')
            a_timebase.text = str(fps)
            a_ntsc = SubElement(a_rate, 'ntsc')
            a_ntsc.text = 'FALSE'
            a_start = SubElement(a_clipitem,'start')
            if (dlg.checkBox_addtransition.isChecked() and k!=0):
                a_start.text = str(video_files[k][2]-(transition_length)/2)

            else:
                a_start.text = str(video_files[k][2])
            a_end = SubElement(a_clipitem,'end')
            if (dlg.checkBox_addtransition.isChecked()):
                a_end.text = str(video_files[k][3]-(transition_length)/2)

            else:
                a_end.text = str(video_files[k][3])
            
            a_in = SubElement(a_clipitem,'in')
            if (dlg.checkBox_addtransition.isChecked() and k!=0):
                a_in.text = str(video_files[k][4]+(transition_length)/2)

            else:
                a_in.text = str(video_files[k][4])
            
            a_out = SubElement(a_clipitem,'out')
            a_out.text = str(video_files[k][5])
            a_file = SubElement(a_clipitem, 'file', id='file-'+str(k+1))
            a_sourcetrack = SubElement(a_clipitem,'sourcetrack')
            a_mediatype = SubElement(a_sourcetrack,'mediatype')
            a_mediatype.text = 'audio'
            a_trackindex = SubElement(a_sourcetrack,'trackindex')
            a_trackindex.text = '1'
            v_link = SubElement(a_clipitem,'link')
            v_linkclipref = SubElement(v_link,'linkclipref')
            v_linkclipref.text = 'clipitem-'+str(k+1)
            v_mediatype = SubElement(v_link,'mediatype')
            v_mediatype.text = 'video'
            v_trackindex = SubElement(v_link,'trackindex')
            v_trackindex.text = '1'
            v_clipindex = SubElement(v_link,'clipindex')
            v_clipindex.text = str(k+2)

            a_link = SubElement(a_clipitem,'link')
            a_linkclipref = SubElement(a_link,'linkclipref')
            a_linkclipref.text = 'clipitem-'+str(total_file+k+1)
            a_mediatype = SubElement(a_link,'mediatype')
            a_mediatype.text = 'audio'
            a_trackindex = SubElement(a_link,'trackindex')
            a_trackindex.text = '1'
            a_clipindex = SubElement(a_link,'clipindex')
            a_clipindex.text = str(k+1)

            k+=1
        
        track5 = SubElement(audio, 'track')
        track5.set('TL.SQTrackAudioKeyframeStyle','0') 
        track5.set('TL.SQTrackShy', '0')
        track5.set('TL.SQTrackExpandedHeight', '25')
        track5.set('TL.SQTrackExpanded', '0')
        track5.set('MZ.TrackTargeted', '1')
        track5.set('PannerCurrentValue','0.5')
        track5.set('PannerIsInverted','true')
        track5.set('PannerStartKeyframe','-91445760000000000,0.5,0,0,0,0,0,0')
        track5.set('PannerName','Balance')
        track5.set('currentExplodedTrackIndex','0')
        track5.set('totalExplodedTrackCount','2')
        track5.set('premiereTrackType','Stereo')

        track6 = SubElement(audio, 'track')
        track6.set('TL.SQTrackAudioKeyframeStyle','0') 
        track6.set('TL.SQTrackShy', '0')
        track6.set('TL.SQTrackExpandedHeight', '25')
        track6.set('TL.SQTrackExpanded', '0')
        track6.set('MZ.TrackTargeted', '1')
        track6.set('PannerCurrentValue','0.5')
        track6.set('PannerIsInverted','true')
        track6.set('PannerStartKeyframe','-91445760000000000,0.5,0,0,0,0,0,0')
        track6.set('PannerName','Balance')
        track6.set('currentExplodedTrackIndex','0')
        track6.set('totalExplodedTrackCount','2')
        track6.set('premiereTrackType','Stereo')

        print('Project file generated successful !!!! check the selected directory')
        prj_duration = end_frame/fps
        min = str(int(prj_duration/60))
        sec = str(int(prj_duration%60))
        msec = prj_duration%1
        msec = str(int(round(msec,2)))
        dlg.lineEdit_pduration.setText(min+' : '+sec+' : '+msec)
        



    def xml_prj(self, dir, files, dlg):
        p_width = str(dlg.lineEdit_width.text())
        p_height = str(dlg.lineEdit_height.text())
        xmeml = Element('xmeml')
        xmeml.set('version', '4')
        comment = Comment('Generated by AutoEditx @uddipan')
        xmeml.append(comment)

        sequence = SubElement(xmeml, 'sequence', id='sequence-1')
        sequence.set('TL.SQAVDividerPosition', '0.5')
        sequence.set('TL.SQHideShyTracks', '0')
        sequence.set('TL.SQHeaderWidth', '236')
        sequence.set('Monitor.ProgramZoomOut', '101063855692800')
        sequence.set('Monitor.ProgramZoomIn', '0')
        sequence.set('TL.SQTimePerPixel', '0.19999999999999998')
        sequence.set('MZ.EditLine', '28444339123200')
        sequence.set('MZ.Sequence.PreviewFrameSizeHeight', '480')
        sequence.set('MZ.Sequence.PreviewFrameSizeWidth', '1080')
        sequence.set('MZ.Sequence.AudioTimeDisplayFormat', '200')
        sequence.set('MZ.Sequence.PreviewRenderingClassID', '1061109567')
        sequence.set('MZ.Sequence.PreviewRenderingPresetCodec', '1685288558')
        sequence.set('MZ.Sequence.PreviewRenderingPresetPath',
                     'EncoderPresets\\SequencePreview\\0f3c7317-cf5d-44e8-8b19-1bc6d7b05ce6\\Microsoft AVI DV NTSC.epr')
        sequence.set('MZ.Sequence.PreviewUseMaxRenderQuality', 'false')
        sequence.set('MZ.Sequence.PreviewUseMaxBitDepth', 'false')
        sequence.set('MZ.Sequence.EditingModeGUID', '0f3c7317-cf5d-44e8-8b19-1bc6d7b05ce6')
        sequence.set('MZ.Sequence.VideoTimeDisplayFormat', '102')
        sequence.set('MZ.WorkOutPoint', '15239249625600')
        sequence.set('MZ.WorkInPoint', '0')
        sequence.set('explodedTracks', 'true')
        sequence.set('TL.SQAudioVisibleBase', '0')

        uuid = SubElement(sequence, 'uuid')
        uuid.text = '3a987937-2043-4812-ac76-47db39d7e9c3'

        duration = SubElement(sequence, 'duration')
        duration.text = '0'
        rate = SubElement(sequence, 'rate')
        timebase = SubElement(rate, 'timebase')
        timebase.text = str(dlg.lineEdit_fps.text())

        ntsc = SubElement(rate, 'ntsc')
        ntsc.text = 'FALSE'
        se_name = SubElement(sequence, 'name')
        se_name.text = 'Sequence 01'
        media = SubElement(sequence, 'media')
        video = SubElement(media, 'video')
        format = SubElement(video, 'format')
        samplecharacteristics = SubElement(format, 'samplecharacteristics')


        rate = SubElement(samplecharacteristics, 'rate')
        timebase = SubElement(rate, 'timebase')
        timebase.text = str(dlg.lineEdit_fps.text())
        ntsc = SubElement(rate, 'ntsc')
        ntsc.text = 'FALSE'

        codec = SubElement(samplecharacteristics, 'codec')
        name = SubElement(codec, 'name')
        name.text = 'Apple ProRes 422'
        appspecificdata = SubElement(codec, 'appspecificdata')
        appname = SubElement(appspecificdata, 'appname')
        appname.text = 'Final Cut Pro'
        appmanufacture = SubElement(appspecificdata, 'appmanufacture')
        appmanufacture.text = 'Apple Inc.'
        appversion = SubElement(appspecificdata, 'appversion')
        appversion.text = '7.0'
        data = SubElement(appspecificdata, 'data')
        qtcodec = SubElement(data, 'qtcodec')
        codecname = SubElement(qtcodec, 'codecname')
        codecname.text = 'Apple ProRes 422'
        codectypename = SubElement(qtcodec, 'codectypename')
        codectypename.text = 'Apple ProRes 422'
        codectypecode = SubElement(qtcodec, 'codectypecode')
        codectypecode.text = 'apcn'
        codecvendorcode = SubElement(qtcodec, 'codecvendorcode')
        codecvendorcode.text = 'appl'
        spatialquality = SubElement(qtcodec, 'spatialquality')
        spatialquality.text = '1024'
        temporalquality = SubElement(qtcodec, 'temporalquality')
        temporalquality.text = '0'
        keyframerate = SubElement(qtcodec, 'keyframerate')
        keyframerate.text = '0'
        datarate = SubElement(qtcodec, 'datarate')
        datarate.text = '0'

        width = SubElement(samplecharacteristics, 'width')
        width.text = p_width
        height = SubElement(samplecharacteristics, 'height')
        height.text = p_height
        anamorphic = SubElement(samplecharacteristics, 'anamorphic')
        anamorphic.text = 'FALSE'
        pixelaspectratio = SubElement(samplecharacteristics, 'pixelaspectratio')
        pixelaspectratio.text = 'square'
        fielddominance = SubElement(samplecharacteristics, 'felddominance')
        fielddominance.text = 'none'
        colordepth = SubElement(samplecharacteristics, 'colordepth')
        colordepth.text = '24'

        track1 = SubElement(video, 'track')
        track1.set('TL.SQTrackShy', '0')
        track1.set('TL.SQTrackExpandedHeight', '25')
        track1.set('TL.SQTrackExpanded', '0')
        track1.set('MZ.TrackTargeted', '1')
        self.clipItem(track1, dir, files, dlg)

        track3 = SubElement(video, 'track')
        track3.set('TL.SQTrackShy', '0')
        track3.set('TL.SQTrackExpandedHeight', '25')
        track3.set('TL.SQTrackExpanded', '0')
        track3.set('MZ.TrackTargeted', '1')
        enabled3 = SubElement(track3, 'enabled')
        enabled3.text = 'TRUE'
        locked3 = SubElement(track3, 'lockeded')
        locked3.text = 'FALSE'
        
        track2 = SubElement(video, 'track')
        track2.set('TL.SQTrackShy', '0')
        track2.set('TL.SQTrackExpandedHeight', '25')
        track2.set('TL.SQTrackExpanded', '0')
        track2.set('MZ.TrackTargeted', '1')
        enabled2 = SubElement(track2, 'enabled')
        enabled2.text = 'TRUE'
        locked2 = SubElement(track2, 'lockeded')
        locked2.text = 'FALSE'

   
        self.audioTrack(media,dlg)


        x = tostring(xmeml)
        filename = dir+'/project.xml'
        f = open(filename, "w+")
        f.write(str(x))
        f.close()
        #p = open("test_xml.xml", "w+")
        #p.write(BeautifulSoup(x, "xml").prettify())
        #p.close()