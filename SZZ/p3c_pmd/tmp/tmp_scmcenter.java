package com.alipay.scmcenter.model.prepub;

import com.alipay.scmcenter.common.dal.dataobject.PrepubTaskDO;

import java.util.Date;

/**
 * Created by Aoming~   on 15/9/14.
 */
public class PrepubTask extends PrepubTaskDO {

    public PrepubTask(String transIdc, String tenantName, String reposName, String projectName, String appName, String prepubBranch, String releaseId, int taskType, int taskStatus, Date taskCreateTime) {
        super(transIdc, tenantName, reposName, projectName, appName, prepubBranch, releaseId, taskType, taskStatus, taskCreateTime);
    }
}

