package com.alibaba.force.base.diff.service.impl;

import java.io.File;
import java.io.IOException;
import java.util.Iterator;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

import javax.validation.constraints.NotNull;

import com.alibaba.force.base.commit.model.dto.output.CommitDTO;
import com.alibaba.force.base.diff.model.dto.DiffDTO;
import com.alibaba.force.base.diff.model.dto.DiffExtendsOidDTO;
import com.alibaba.force.base.diff.model.query.CommitDiffQuery;
import com.alibaba.force.base.diff.service.Diffs;
import com.alibaba.force.base.grpc.DiffClient;
import com.alibaba.force.common.service.CmdExec;
import com.alibaba.force.common.service.impl.CmdExecImpl;
import com.alibaba.force.common.service.model.CmdExecResult;
import com.alibaba.force.common.exception.http.ForceRunTimeException;
import com.alibaba.force.common.util.CollectionUtils;
import com.alibaba.force.common.util.Constants;
import com.alibaba.force.common.util.PropertyUtils;
import com.alibaba.force.grpc.Diff.CommitDiffResponse;

import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.FileUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

/**
 * Created by keriezhang on 2017/11/8.
 *
 * @author keriezhang
 * @date 2017/11/8
 */
@Slf4j
@Service
public class DiffsImpl implements Diffs {

    @Override
    public List<DiffDTO> getCommitDiff(CommitDTO singleCommit, String absolutePath) {
        return this.getCommitDiff(singleCommit, absolutePath, null);
    }

    @Override
    public List<DiffDTO> getCommitDiff(CommitDTO singleCommit, String absolutePath, List<String> paths) {
        List<String> parentIds = singleCommit.getParentIds();
        CommitDiffQuery query = new CommitDiffQuery();
        query.setAbsolutePath(absolutePath);
        if (CollectionUtils.isNotEmpty(paths)) {
            query.setPaths(paths);
        }
        String fromId = CollectionUtils.isEmpty(parentIds) ? Constants.BRANCH_BLANK_SHA : parentIds.get(0);
        query.setLeftCommitId(fromId);
        query.setRightCommitId(singleCommit.getId());

        List<CommitDiffResponse> originDiffList = diffClient.commitDiff(query);
        return originDiffList.stream().map(DiffDTO::new).collect(Collectors.toList());
    }

    @Override
    public List<DiffExtendsOidDTO> compare(CommitDTO from, CommitDTO to, String absolutePath, Boolean useMergeBase,
        Integer contextLine) {
        CommitDiffQuery query = new CommitDiffQuery();
        query.setAbsolutePath(absolutePath);
        query.setLeftCommitId(from.getId());
        query.setRightCommitId(to.getId());
        query.setUserMergeBase(useMergeBase);
        query.setContextLine(contextLine);
        List<CommitDiffResponse> originDiffList = diffClient.commitDiff(query);
        return originDiffList.stream().map(DiffExtendsOidDTO::new).collect(Collectors.toList());
    }

    @Override
    public String compareFileContent(@NotNull String oldFileName, @NotNull String newFileName,
        @NotNull String oldFileContent,
        @NotNull String newFileContent) throws IOException {

        // 1. 新建临时目录
        File dir = getRandomDir();
        List<String> rawDiffList;
        try {
            // 2. 写入临时文件
            // oldFileName newFileName可能是多级路径，不再解析，而是生成随机的文件名
            File tmpOldFile = new File(dir, UUID.randomUUID().toString());
            File tmpNewFile = new File(dir, UUID.randomUUID().toString());
            FileUtils.writeStringToFile(tmpOldFile, oldFileContent, PropertyUtils.getForceDefaultEncoding());
            FileUtils.writeStringToFile(tmpNewFile, newFileContent, PropertyUtils.getForceDefaultEncoding());
            // 3. diff对比
            String diffCmd = String.format(DIFF_TEMPLATE, tmpOldFile.getCanonicalPath(), tmpNewFile.getCanonicalPath());
            CmdExecResult cmdExecResult = cmdExec.exec(diffCmd, DIFF_MAX_WAIT_SECOND , TimeUnit.SECONDS);
            if (cmdExecResult.getExitValue().intValue() != CmdExecImpl.SUCCESSFUL_EXIT.intValue()) {
                StringBuilder stringBuilder = new StringBuilder(128);
                cmdExecResult.getStdErr().forEach(s -> stringBuilder.append(s));
                String errorMessage = "Diff command run fail. Cmd:" + diffCmd + ". exitCode:" + cmdExecResult
                    .getExitValue();
                log.error(errorMessage + stringBuilder.toString());
                throw new IOException(errorMessage);
            }
            rawDiffList = cmdExecResult.getStdOut();
        } catch (Exception e) {
            log.error(e.getMessage(), e);
            throw new IOException(e);
        } finally {
            // 4. 删除临时文件
            FileUtils.deleteDirectory(dir);
        }

        /**
         * 如果diff对比正常，转化为git diff header格式
         * --- buqiong.tx	2018-04-19 19:41:30.000000000 +0800
         +++ buqiong.txt	2018-04-18 17:56:30.000000000 +0800
         ->
         --- a/buqiong.tx
         +++ b/buqiong.txt
         */

        if (rawDiffList.size() >= difflib.Constants.MIN_DIFF_LINE && rawDiffList.get(0).startsWith(difflib.Constants.FIRST_LINE_PREFIX) && rawDiffList.get(
            1).startsWith(difflib.Constants.SECOND_LINE_PREFIX)) {
            rawDiffList.set(0, difflib.Constants.FIRST_LINE_PREFIX + difflib.Constants.GIT_FORMAT_FIRST_LINE_FILE_PREFIX + oldFileName);
            rawDiffList.set(0, difflib.Constants.SECOND_LINE_PREFIX + difflib.Constants.GIT_FORMAT_SECOND_LINE_FILE_PREFIX + newFileName);
        }

        Iterator<String> iterator = rawDiffList.iterator();
        StringBuilder stringBuilder = new StringBuilder(1024);
        while (iterator.hasNext()){
            String line = iterator.next();
            if(!line.startsWith(Constants.BACK_SLASH)){
                stringBuilder.append(line);
                if(iterator.hasNext()){
                    stringBuilder.append(Constants.RETURN);
                }
            }
        }
        return stringBuilder.toString();
    }

    /**
     * 尝试3次，创建一个随机名称的目录
     *
     * @return
     */
    private File getRandomDir() {
        for (int i = 3; i > 0; i--) {
            String dirPath = PropertyUtils.getRootDiff() + UUID.randomUUID();
            File file = new File(dirPath);
            if (!file.exists() && file.mkdirs() && file.isDirectory()) {
                return file;
            }
        }
        throw new ForceRunTimeException("Cannot create a random Dir, try 3 times failed.");
    }

    private DiffClient diffClient;
    private CmdExec cmdExec;
    private static final String DIFF_TEMPLATE = "diff -U65535 -bw %s %s";
    private static final Long DIFF_MAX_WAIT_SECOND = 20L;

    @Autowired
    public DiffsImpl(DiffClient diffClient, CmdExec cmdExec) {
        this.diffClient = diffClient;
        this.cmdExec = cmdExec;
    }
}
